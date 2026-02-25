// src/lib/device.js
import { writable } from 'svelte/store'

// reactive viewport info
function getViewport() {
  return {
    width: window.innerWidth,
    height: window.innerHeight,
    orientation: window.innerWidth > window.innerHeight ? 'landscape' : 'portrait'
  }
}

export const viewport = writable(getViewport())

window.addEventListener('resize', () => {
  viewport.set(getViewport())
})

// device info
export const Device = {
  isMobile: /Mobi|Android/i.test(navigator.userAgent),
  isTablet: /Tablet|iPad/i.test(navigator.userAgent),
  isDesktop: !/Mobi|Android|Tablet|iPad/i.test(navigator.userAgent),

  os: (() => {
    const ua = navigator.userAgent
    if (/Windows/i.test(ua)) return 'Windows'
    if (/Mac/i.test(ua)) return 'Mac'
    if (/Linux/i.test(ua)) return 'Linux'
    if (/Android/i.test(ua)) return 'Android'
    if (/iPhone|iPad|iPod/i.test(ua)) return 'iOS'
    return 'Unknown'
  })(),

  browser: (() => {
    const ua = navigator.userAgent
    if (/Chrome/i.test(ua) && !/Edg/i.test(ua)) return 'Chrome'
    if (/Firefox/i.test(ua)) return 'Firefox'
    if (/Safari/i.test(ua) && !/Chrome/i.test(ua)) return 'Safari'
    if (/Edg/i.test(ua)) return 'Edge'
    return 'Unknown'
  })()
}