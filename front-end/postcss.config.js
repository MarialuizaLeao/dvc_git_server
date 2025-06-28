export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {
      overrideBrowserslist: [
        'Chrome >= 54',
        'ChromeAndroid >= 54',
        'Edge >= 79',
        'Firefox >= 60',
        'Safari >= 12',
        'iOS >= 12'
      ]
    },
  },
}
