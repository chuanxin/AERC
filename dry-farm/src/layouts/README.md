# Layouts

Layouts are reusable components that wrap around pages. They are used to provide a consistent look and feel across multiple pages.

Full documentation for this feature can be found in the Official [vite-plugin-vue-layouts](https://github.com/JohnCampionJr/vite-plugin-vue-layouts) repository.

# Layouts Directory

Layout components are used to wrap page content:
- default.vue: Default layout, automatically applied to pages without specified layout
- custom.vue: Custom layouts can be specified in page components using layout syntax

The <router-view /> in layouts is used to render page content.

## Structure
- Layouts provide consistent UI elements across pages
- Common elements like navigation bars, footers
- Nested routing support through router-view
- Flexible layout switching based on routes

## Usage
Pages will be automatically wrapped in layouts through the auto-routing system.
See router/index.ts for the implementation details.