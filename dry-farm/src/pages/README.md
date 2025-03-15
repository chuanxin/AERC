# Pages

Vue components created in this folder will automatically be converted to navigatable routes.

Full documentation for this feature can be found in the Official [unplugin-vue-router](https://github.com/posva/unplugin-vue-router) repository.

# Pages Directory

Vue files in this directory are automatically converted to routes:
- index.vue -> '/'
- about.vue -> '/about'
- users/[id].vue -> '/users/:id'

File naming directly affects route paths.

## Structure
- Single file components
- Automatic route generation
- Dynamic route parameters supported
- Nested routing through directory structure

## Usage
Pages are rendered within layouts through the router-view component.