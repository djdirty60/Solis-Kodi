package nl.leek.solis.tv

import android.app.Activity
import android.graphics.Color
import android.os.Bundle
import android.text.InputType
import android.view.ViewGroup
import android.widget.Button
import android.widget.CheckBox
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView

/** Instellingen: het adres van de Homey en het doorbladeren. */
class SettingsActivity : Activity() {
    private lateinit var store: Store
    private lateinit var hostEdit: EditText
    private lateinit var portEdit: EditText
    private lateinit var rotateBox: CheckBox
    private lateinit var secEdit: EditText
    private lateinit var result: TextView
    private lateinit var searchBtn: Button
    private lateinit var testBtn: Button
    private lateinit var saveBtn: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        store = Store(this)

        val col = LinearLayout(this)
        col.orientation = LinearLayout.VERTICAL
        col.setPadding(dp(64), dp(40), dp(64), dp(40))

        col.addView(text("Solis - instellingen", 30f, true))
        col.addView(text("Vul het adres in van je Homey (of van de computer waarop het dashboard draait).", 18f, false))

        col.addView(text("Adres", 18f, true))
        hostEdit = edit("homey.local of bijvoorbeeld 192.168.178.20", InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_URI)
        hostEdit.setText(store.host)
        col.addView(hostEdit)

        col.addView(text("Poort (meestal 8765)", 18f, true))
        portEdit = edit("8765", InputType.TYPE_CLASS_NUMBER)
        portEdit.setText(store.port.toString())
        col.addView(portEdit)

        searchBtn = button("Zoek zelf in mijn netwerk")
        searchBtn.setOnClickListener { search() }
        col.addView(searchBtn)

        testBtn = button("Test de verbinding")
        testBtn.setOnClickListener { test() }
        col.addView(testBtn)

        result = text("", 18f, false)
        col.addView(result)

        rotateBox = CheckBox(this)
        rotateBox.text = "Automatisch doorbladeren"
        rotateBox.setTextColor(Color.WHITE)
        rotateBox.textSize = 20f
        rotateBox.isChecked = store.rotate
        col.addView(rotateBox)

        col.addView(text("Seconden per pagina (5 tot 600)", 18f, true))
        secEdit = edit("20", InputType.TYPE_CLASS_NUMBER)
        secEdit.setText(store.rotateSec.toString())
        col.addView(secEdit)

        saveBtn = button("Opslaan")
        saveBtn.setOnClickListener { save() }
        col.addView(saveBtn)

        val scroll = ScrollView(this)
        scroll.addView(col, ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT))
        scroll.setBackgroundColor(Color.parseColor("#0E1220"))
        setContentView(scroll)
    }

    private fun dp(v: Int): Int = (v * resources.displayMetrics.density).toInt()

    private fun text(t: String, size: Float, bold: Boolean): TextView {
        val v = TextView(this)
        v.text = t
        v.textSize = size
        v.setTextColor(Color.WHITE)
        if (bold) v.setTypeface(v.typeface, android.graphics.Typeface.BOLD)
        v.setPadding(0, dp(14), 0, dp(4))
        return v
    }

    private fun edit(hintText: String, type: Int): EditText {
        val e = EditText(this)
        e.hint = hintText
        e.inputType = type
        e.setSingleLine(true)
        e.textSize = 22f
        e.setTextColor(Color.WHITE)
        e.setHintTextColor(Color.parseColor("#80FFFFFF"))
        return e
    }

    private fun button(label: String): Button {
        val b = Button(this)
        b.text = label
        b.textSize = 18f
        val lp = LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT)
        lp.topMargin = dp(12)
        b.layoutParams = lp
        return b
    }

    private fun showResult(msg: String) {
        runOnUiThread {
            if (!isFinishing) result.text = msg
        }
    }

    private fun busy(on: Boolean) {
        runOnUiThread {
            searchBtn.isEnabled = !on
            testBtn.isEnabled = !on
            saveBtn.isEnabled = !on
        }
    }

    private fun portValue(): Int? {
        val p = portEdit.text.toString().trim().toIntOrNull()
        return if (p != null && p in 1..65535) p else null
    }

    private fun search() {
        val port = portValue()
        if (port == null) {
            result.text = "De poort moet een getal zijn tussen 1 en 65535."
            return
        }
        val prefix = Net.localPrefix(this)
        if (prefix == null) {
            result.text = "Ik zie geen netwerk. Is de tv met wifi of kabel verbonden?"
            return
        }
        busy(true)
        result.text = "Bezig met zoeken in $prefix... Dit duurt maximaal een minuut."
        Thread {
            var found: String? = null
            try {
                found = if (Net.probe("homey.local", port, 800, 1200)) "homey.local" else Net.scan(prefix, port)
            } catch (e: Throwable) {
                found = null
            }
            val f = found
            runOnUiThread {
                if (!isFinishing) {
                    if (f != null) {
                        hostEdit.setText(f)
                        result.text = "Gevonden: $f. Druk op Opslaan."
                    } else {
                        result.text = "Niets gevonden op poort $port. Controleer of de dashboard-instelling in de Solis-app aanstaat, " +
                            "of vul het adres zelf in."
                    }
                }
            }
            busy(false)
        }.start()
    }

    private fun test() {
        val host = hostEdit.text.toString().trim()
        val port = portValue()
        if (host.isEmpty()) {
            result.text = "Vul eerst een adres in."
            return
        }
        if (port == null) {
            result.text = "De poort moet een getal zijn tussen 1 en 65535."
            return
        }
        busy(true)
        result.text = "Verbinding testen..."
        Thread {
            val msg = try {
                val list = Net.fetchPages(Net.baseUrl(host, port), 4000, 6000)
                "Gelukt. Ik zie ${list.size} pagina's."
            } catch (e: java.net.UnknownHostException) {
                "Ik kan '$host' niet vinden. Probeer het IP-adres van je Homey."
            } catch (e: java.net.SocketTimeoutException) {
                "Geen antwoord (te lang gewacht). Klopt het adres en staat de Homey aan?"
            } catch (e: java.net.ConnectException) {
                "Verbinding geweigerd. Klopt de poort, en staat het dashboard aan in de Solis-app?"
            } catch (e: Throwable) {
                "Dat lukte niet: ${e.message ?: e.javaClass.simpleName}"
            }
            showResult(msg)
            busy(false)
        }.start()
    }

    private fun save() {
        val host = hostEdit.text.toString().trim()
        val port = portValue()
        val sec = secEdit.text.toString().trim().toIntOrNull()
        if (host.isEmpty()) {
            result.text = "Vul eerst een adres in."
            return
        }
        if (port == null) {
            result.text = "De poort moet een getal zijn tussen 1 en 65535."
            return
        }
        if (sec == null || sec < 5 || sec > 600) {
            result.text = "Seconden per pagina: kies een getal van 5 tot 600."
            return
        }
        store.host = host
        store.port = port
        store.rotate = rotateBox.isChecked
        store.rotateSec = sec
        finish()
    }

}
