package nl.leek.solis.tv

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.view.KeyEvent
import android.view.View
import android.view.WindowManager

/** Het gewone scherm: de Solis-pagina's op de tv. */
class MainActivity : Activity() {
    private lateinit var store: Store
    private var viewer: SolisViewer? = null
    private var askedSettings = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        store = Store(this)
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
    }

    override fun onResume() {
        super.onResume()
        if (!store.configured) {
            if (askedSettings) {
                finish()
                return
            }
            askedSettings = true
            startActivity(Intent(this, SettingsActivity::class.java))
            return
        }
        askedSettings = false
        val v = SolisViewer(this, store, false) {
            startActivity(Intent(this, SettingsActivity::class.java))
        }
        viewer = v
        setContentView(v.root)
        v.start()
        Updater.checkOnStart(this)
    }

    override fun onPause() {
        viewer?.stop()
        viewer = null
        super.onPause()
    }

    override fun onWindowFocusChanged(hasFocus: Boolean) {
        super.onWindowFocusChanged(hasFocus)
        if (hasFocus) hideSystemUi()
    }

    @Suppress("DEPRECATION")
    private fun hideSystemUi() {
        window.decorView.systemUiVisibility = (View.SYSTEM_UI_FLAG_FULLSCREEN
                or View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                or View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                or View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                or View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                or View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN)
    }

    override fun onKeyDown(keyCode: Int, event: KeyEvent?): Boolean {
        if (viewer?.handleKey(keyCode) == true) return true
        return super.onKeyDown(keyCode, event)
    }
}
