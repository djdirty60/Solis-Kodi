package nl.leek.solis.tv

import android.app.Activity
import android.app.AlertDialog
import android.app.PendingIntent
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.pm.PackageInstaller
import android.net.Uri
import android.os.Build
import android.os.Handler
import android.os.Looper
import android.provider.Settings
import android.widget.Toast
import org.json.JSONObject
import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL

/**
 * Updater: kijkt op GitHub (tv-apps/versie.json) of er een nieuwere versie van deze app is.
 * Zo ja: vraagt of je wilt bijwerken, downloadt de nieuwe APK en opent het installatiescherm van Android.
 * Android laat een app zichzelf niet stilletjes vervangen: op dat scherm druk je zelf nog op Installeren.
 */
object Updater {
    private const val INFO_URL = "https://raw.githubusercontent.com/djdirty60/Solis-Kodi/main/tv-apps/versie.json"
    private const val PREFS = "solis-update"
    const val ACTION = "nl.leek.solis.tv.UPDATE_STATUS"

    class Info(val code: Long, val name: String, val apk: String, val note: String)

    private val main = Handler(Looper.getMainLooper())

    fun currentCode(ctx: Context): Long {
        val pi = ctx.packageManager.getPackageInfo(ctx.packageName, 0)
        return if (Build.VERSION.SDK_INT >= 28) pi.longVersionCode else {
            @Suppress("DEPRECATION")
            pi.versionCode.toLong()
        }
    }

    private fun get(url: String, readMs: Int): HttpURLConnection {
        val c = URL(url).openConnection() as HttpURLConnection
        c.connectTimeout = 8000
        c.readTimeout = readMs
        c.useCaches = false
        c.instanceFollowRedirects = true
        c.setRequestProperty("Cache-Control", "no-cache")
        return c
    }

    /** Haalt de versie-informatie op (in een achtergronddraad aanroepen). Null = geen nieuwere versie. */
    fun check(ctx: Context): Info? {
        val c = get(INFO_URL + "?t=" + System.currentTimeMillis(), 8000)
        try {
            if (c.responseCode != 200) return null
            val body = c.inputStream.bufferedReader().use { it.readText() }
            val a = JSONObject(body).getJSONObject("android")
            val info = Info(a.getLong("versionCode"), a.optString("versionName", ""), a.getString("apk"), a.optString("nieuw", ""))
            return if (info.code > currentCode(ctx)) info else null
        } finally {
            c.disconnect()
        }
    }

    /** Bij het opstarten: hooguit eens per 6 uur kijken, en een melding tonen als er iets nieuws is. */
    fun checkOnStart(act: Activity, force: Boolean = false) {
        val prefs = act.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        val last = prefs.getLong("lastCheck", 0L)
        if (!force && System.currentTimeMillis() - last < 6 * 3600 * 1000L) return
        Thread {
            val info = try { check(act) } catch (e: Exception) { null }
            prefs.edit().putLong("lastCheck", System.currentTimeMillis()).apply()
            main.post {
                if (act.isFinishing) return@post
                if (info != null) ask(act, info)
                else if (force) Toast.makeText(act, "Je hebt de nieuwste versie.", Toast.LENGTH_LONG).show()
            }
        }.start()
    }

    private fun ask(act: Activity, info: Info) {
        val text = "Versie " + info.name + " staat klaar." + (if (info.note.isNotBlank()) "\n\n" + info.note else "") +
            "\n\nNu bijwerken? Daarna vraagt de tv nog één keer of je wilt installeren."
        AlertDialog.Builder(act)
            .setTitle("Nieuwe versie van Solis")
            .setMessage(text)
            .setPositiveButton("Bijwerken") { _, _ -> start(act, info) }
            .setNegativeButton("Later", null)
            .show()
    }

    private fun start(act: Activity, info: Info) {
        // Eerst moet deze app apps mogen installeren (eenmalige toestemming in de instellingen van de tv)
        if (Build.VERSION.SDK_INT >= 26 && !act.packageManager.canRequestPackageInstalls()) {
            Toast.makeText(act, "Zet 'Apps installeren toestaan' aan voor Solis, ga terug en kies opnieuw Bijwerken.", Toast.LENGTH_LONG).show()
            act.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().putLong("lastCheck", 0L).apply()
            try {
                act.startActivity(Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES, Uri.parse("package:" + act.packageName)))
            } catch (e: Exception) {
                Toast.makeText(act, "Zet in de instellingen van de tv 'Onbekende apps installeren' aan voor Solis.", Toast.LENGTH_LONG).show()
            }
            return
        }
        Toast.makeText(act, "Nieuwe versie downloaden...", Toast.LENGTH_LONG).show()
        val app = act.applicationContext
        Thread {
            try {
                install(app, info)
            } catch (e: Exception) {
                main.post { Toast.makeText(app, "Bijwerken mislukt: " + (e.message ?: e.javaClass.simpleName), Toast.LENGTH_LONG).show() }
            }
        }.start()
    }

    /** Download de APK rechtstreeks in een installatiesessie van Android en rond die af. */
    private fun install(ctx: Context, info: Info) {
        val installer = ctx.packageManager.packageInstaller
        val params = PackageInstaller.SessionParams(PackageInstaller.SessionParams.MODE_FULL_INSTALL)
        params.setAppPackageName(ctx.packageName)
        val id = installer.createSession(params)
        val session = installer.openSession(id)
        try {
            val c = get(info.apk, 60000)
            try {
                if (c.responseCode != 200) throw IOException("download gaf HTTP " + c.responseCode)
                val total = c.contentLength.toLong()
                c.inputStream.use { input ->
                    session.openWrite("solis.apk", 0, if (total > 0) total else -1).use { out ->
                        input.copyTo(out, 64 * 1024)
                        session.fsync(out)
                    }
                }
            } finally {
                c.disconnect()
            }
            val intent = Intent(ctx, InstallReceiver::class.java).setAction(ACTION)
            var flags = PendingIntent.FLAG_UPDATE_CURRENT
            if (Build.VERSION.SDK_INT >= 31) flags = flags or PendingIntent.FLAG_MUTABLE
            val pi = PendingIntent.getBroadcast(ctx, id, intent, flags)
            session.commit(pi.intentSender)
        } catch (e: Exception) {
            session.abandon()
            throw e
        } finally {
            session.close()
        }
    }
}

/** Ontvangt de uitslag van de installatie en opent zo nodig het bevestigingsscherm van Android. */
class InstallReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        when (intent.getIntExtra(PackageInstaller.EXTRA_STATUS, PackageInstaller.STATUS_FAILURE)) {
            PackageInstaller.STATUS_PENDING_USER_ACTION -> {
                @Suppress("DEPRECATION")
                val confirm = intent.getParcelableExtra<Intent>(Intent.EXTRA_INTENT)
                if (confirm != null) {
                    confirm.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                    context.startActivity(confirm)
                }
            }
            PackageInstaller.STATUS_SUCCESS -> Toast.makeText(context, "Solis is bijgewerkt.", Toast.LENGTH_LONG).show()
            else -> {
                val msg = intent.getStringExtra(PackageInstaller.EXTRA_STATUS_MESSAGE) ?: "onbekende fout"
                Toast.makeText(context, "Bijwerken mislukt: $msg", Toast.LENGTH_LONG).show()
            }
        }
    }
}
