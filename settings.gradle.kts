pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "uaim_projekt"

// Dołączamy moduł mobilny do głównego projektu
include(":app")
project(":app").projectDir = file("mobile/app")
