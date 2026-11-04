plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "nl.leek.solis.tv"
    compileSdk = 34

    defaultConfig {
        applicationId = "nl.leek.solis.tv"
        minSdk = 23
        targetSdk = 34
        versionCode = 3
        versionName = "1.2.0"
    }

    // Altijd dezelfde handtekening, zodat een nieuwe versie gewoon over de oude heen installeert.
    signingConfigs {
        getByName("debug") {
            storeFile = file("solis-debug.keystore")
            storePassword = "android"
            keyAlias = "androiddebugkey"
            keyPassword = "android"
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
}

// Bewust geen extra libraries: alles is gewoon Android zelf.
dependencies {
}
