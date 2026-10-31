# iPhone Home Screen top blur — researched October 31, 2026

## What is known

A website opened from an iPhone Home Screen icon can run as an installed, standalone web app. Its system status-bar treatment can differ from opening the same site inside Safari. **A blurred strip is not an unavoidable feature of every saved bookmark.** It is an OS/version/install-context issue reported for particular Home Screen web-app configurations.

Andrew reports a blurred band over the top of the Running Routes title in the installed app, including after the first `safe-area-inset-top` adjustment. His exact iOS version and current inset measurements have not been obtained. The previous desktop Chrome safe-area emulation verified the CSS movement but did not reproduce the iPhone compositor; it was not proof of a native fix.

## Primary evidence and its limits

- [Actual Budget issue #8899](https://github.com/actualbudget/actual/issues/8899), opened September 7, 2026, documents an iOS 27 Home Screen web-app fade covering top text. The reporter says it remained in the first public iOS 27 release. Maintainers describe moving content away from the top as a mitigation. This is a first-hand application report, not an Apple guarantee that every iOS version behaves identically.
- [WebKit bug #317153](https://bugs.webkit.org/show_bug.cgi?id=317153), an iOS 27 fullscreen/status-bar regression, includes an Apple/WebKit engineer's guidance that `black-translucent` is deprecated and the status bar should follow the page's color without that key. The fullscreen regression is marked fixed; that does **not** establish that the separate top-fade reports are fixed. Other reporters describe different viewport/inset results depending on when the Home Screen icon was installed, including a zero top inset.
- [WebKit bug #301994](https://bugs.webkit.org/show_bug.cgi?id=301994) records iOS 26.1 installed-web-app status-area behavior and reports where the native status area already consumes space while the CSS top inset is zero. The discussion contains differing reproduction results. It supports treating inset values and installed mode as device-specific rather than assuming Safari and Home Screen are identical.
- [OpenCode issue #56969](https://github.com/anomalyco/opencode/issues/56969), opened October 19, 2026, describes the iPadOS 27 installed-app blur reaching its tab strip. Its app already uses an additional 16px clearance on phones; the report concerns missing clearance on wider installed layouts. This is supporting implementation evidence for a buffer, not an official web API for disabling system blur.

## Changes in this app

1. Keep matching opaque white page/theme backgrounds and existing `safe-area-inset-top` padding.
2. Add **16px of extra clearance only for standalone WebKit touch browsers**, leaving normal desktop and Safari-tab layout space unchanged. This moves important text below the reported fade rather than pretending CSS can disable a native compositor effect.
3. Restore the visible Running Routes title and keep counts/mapped-mileage stats below the clearance. Video mode has no run/ride header metrics or redundant introductory heading.
4. Remove the legacy `apple-mobile-web-app-status-bar-style` meta tag. Its old value here was `default`, **not** `black-translucent`, so this cleanup is not asserted to cure the reported blur.
5. Add an explicit full-page Refresh action. HTML responses use `Cache-Control: no-store`; hashed JS/CSS assets remain versioned. Refresh gets current app code and data, rather than merely re-querying Strava.

## What still needs a real-device check

Verify the installed app on Andrew's iPhone after loading this release: title readability, actual safe-area behavior, portrait/landscape, and that the added clearance does not create an excessive gap. Chrome emulation cannot verify the iOS-only fade. If it persists, obtain the iOS version and an installed-app screenshot before adding more padding or changing fullscreen metadata again.

Some WebKit reporters say installation-time chrome can persist. Reloading code does not promise to reset iOS's stored installation settings. Re-adding the Home Screen icon can be a later diagnostic if needed; it is not required here and has not been done automatically.
