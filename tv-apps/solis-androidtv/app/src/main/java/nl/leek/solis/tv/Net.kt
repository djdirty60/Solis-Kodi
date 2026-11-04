package nl.leek.solis.tv

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.ConnectivityManager
import org.json.JSONObject
import java.io.IOException
import java.net.HttpURLConnection
import java.net.Inet4Address
import java.net.URL
import java.util.concurrent.CountDownLatch
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicReference

/** Alle netwerkwerk. Roep dit nooit aan vanuit de hoofdthread. */
object Net {

    fun baseUrl(host: String, port: Int): String {
        val h = host.trim().removePrefix("http://").removePrefix("https://").trimEnd('/')
        return if (h.contains(":")) "http://$h" else "http://$h:$port"
    }

    private fun open(url: String, connectMs: Int, readMs: Int): HttpURLConnection {
        val c = URL(url).openConnection() as HttpURLConnection
        c.connectTimeout = connectMs
        c.readTimeout = readMs
        c.useCaches = false
        c.instanceFollowRedirects = true
        c.setRequestProperty("Cache-Control", "no-cache")
        return c
    }

    /** De lijst met pagina's uit de Solis-app, bijvoorbeeld ["zon","stroom",...]. */
    fun fetchPages(base: String, connectMs: Int = 4000, readMs: Int = 6000): List<String> {
        val c = open("$base/beeld/pages.json", connectMs, readMs)
        try {
            if (c.responseCode != 200) throw IOException("HTTP ${c.responseCode}")
            val text = c.inputStream.bufferedReader().use { it.readText() }
            val arr = JSONObject(text).getJSONArray("pages")
            val out = ArrayList<String>()
            for (i in 0 until arr.length()) {
                val s = arr.optString(i, "")
                if (s.isNotEmpty() && s.all { it in 'a'..'z' }) out.add(s)
            }
            if (out.isEmpty()) throw IOException("lege paginalijst")
            return out
        } finally {
            c.disconnect()
        }
    }

    /** Het plaatje van een pagina (1920x1080 PNG). */
    fun fetchBitmap(base: String, page: String, query: String = ""): Bitmap {
        val c = open("$base/beeld/page/$page.png$query", 4000, 15000)
        try {
            if (c.responseCode != 200) throw IOException("HTTP ${c.responseCode}")
            val bmp = c.inputStream.use { BitmapFactory.decodeStream(it) }
            return bmp ?: throw IOException("geen geldige afbeelding")
        } finally {
            c.disconnect()
        }
    }

    /** Is dit een Solis-app? (Antwoordt het adres met een paginalijst?) */
    fun probe(host: String, port: Int, connectMs: Int, readMs: Int): Boolean {
        return try {
            fetchPages(baseUrl(host, port), connectMs, readMs).isNotEmpty()
        } catch (e: Exception) {
            false
        }
    }

    /** Het begin van het eigen adres van de tv, bijvoorbeeld "192.168.178.". */
    fun localPrefix(context: Context): String? {
        return try {
            val cm = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
            val network = cm.activeNetwork ?: return null
            val props = cm.getLinkProperties(network) ?: return null
            for (la in props.linkAddresses) {
                val ip = la.address
                if (ip is Inet4Address && !ip.isLoopbackAddress) {
                    val s = ip.hostAddress ?: continue
                    return s.substring(0, s.lastIndexOf('.') + 1)
                }
            }
            null
        } catch (e: Exception) {
            null
        }
    }

    /** Zoekt in het hele /24-netwerk naar een Solis-app. Blokkeert tot 60 seconden. */
    fun scan(prefix: String, port: Int): String? {
        val pool = Executors.newFixedThreadPool(48)
        val found = AtomicReference<String?>(null)
        val latch = CountDownLatch(254)
        for (i in 1..254) {
            pool.execute {
                try {
                    if (found.get() == null) {
                        val ip = "$prefix$i"
                        if (probe(ip, port, 500, 900)) found.compareAndSet(null, ip)
                    }
                } catch (e: Exception) {
                    // overslaan
                } finally {
                    latch.countDown()
                }
            }
        }
        try {
            latch.await(60, TimeUnit.SECONDS)
        } catch (e: InterruptedException) {
            // klaar
        }
        pool.shutdownNow()
        return found.get()
    }
}
