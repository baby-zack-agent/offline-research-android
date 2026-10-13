plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
}

android {
    namespace = "com.offlineresearch.app"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.offlineresearch.app"
        minSdk = 26          // GrapheneOS-supported baseline; FTS5 available in bundled SQLite
        targetSdk = 34
        versionCode = 1
        versionName = "1.0.0"
        // The knowledge pack ships as a compressed asset; see PackManager.
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }

    buildFeatures { compose = true }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }

    // NOTE: deliberately NO dependency on com.google.android.gms / Play Services.
    // Core offline research path must never require Google services.
}

dependencies {
    val composeBom = platform("androidx.compose:compose-bom:2024.10.00")
    implementation(composeBom)
    androidTestImplementation(composeBom)

    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.activity:activity-compose:1.9.2")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.8.6")
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-graphics")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")
    // Local unit tests for the engine mirror (no device needed):
    testImplementation("junit:junit:4.13.2")
}
