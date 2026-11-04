package nl.leek.solis.tv

import android.graphics.Color
import android.service.dreams.DreamService
import android.view.Gravity
import android.widget.TextView

/** Schermbeveiliging: de Solis-pagina's op de tv als je niets kijkt. */
class SolisDream : DreamService() {
    private var viewer: SolisViewer? = null

    override fun onAttachedToWindow() {
        super.onAttachedToWindow()
        isInteractive = false
        isFullscreen = true
        val store = Store(this)
        if (!store.configured) {
            val t = TextView(this)
            t.text = "Open eerst de Solis-app op de tv en vul het adres van je Homey in."
            t.setTextColor(Color.WHITE)
            t.textSize = 24f
            t.gravity = Gravity.CENTER
            t.setBackgroundColor(Color.parseColor("#0E1220"))
            setContentView(t)
            return
        }
        val v = SolisViewer(this, store, true)
        viewer = v
        setContentView(v.root)
    }

    override fun onDreamingStarted() {
        super.onDreamingStarted()
        viewer?.start()
    }

    override fun onDreamingStopped() {
        viewer?.stop()
        super.onDreamingStopped()
    }

    override fun onDetachedFromWindow() {
        viewer?.stop()
        viewer = null
        super.onDetachedFromWindow()
    }
}
