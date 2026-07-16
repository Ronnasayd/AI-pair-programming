---
description: Vue SFC rules — English content, multi-word component names, typed props via defineProps, keyed v-for, no v-if+v-for on same element, scoped styles, one component per file, naming conventions (Base/App prefix, parent-prefix for children, general-to-specific), self-closing tags, simple template expressions, split computed properties. Apply to any .vue file. Do NOT use for React (see react.instructions.md).
applyTo: "**/*.vue"
---

# Vue Code Standards

## Quick rules

| Rule                                                        | ✅ Good                                                         | ❌ Bad                                          |
| ----------------------------------------------------------- | --------------------------------------------------------------- | ----------------------------------------------- |
| English everywhere (names, comments, template content)      | `const isUserLoggedIn = ref(false)`                             | `const estaLogado = ref(false)`                 |
| Multi-word component names (avoid HTML tag collision)       | `UserProfile.vue`                                               | `Profile.vue`                                   |
| Detailed prop definitions — type, required, default         | `defineProps<Props>()` with `interface Props {...}`             | `defineProps(["status", "userId"])`             |
| Keyed `v-for`, never loop index as key                      | `v-for="user in users" :key="user.id"`                          | `v-for="(user, i) in users" :key="i"`           |
| Scoped styles                                               | `<style scoped>`                                                | `<style>` (leaks globally)                      |
| One component per `.vue` file                               | `UserCard.vue`, `UserAvatar.vue` separate                       | multiple components in one `.vue` file          |
| Consistent SFC filename casing project-wide                 | all PascalCase or all kebab-case                                | mixed: `UserCard.vue` + `user-profile.vue`      |
| Base/presentational components share a prefix               | `BaseButton.vue`, `BaseInput.vue`                               | `Button.vue`, `MyButton.vue`                    |
| Child components prefixed with parent name                  | `TodoList.vue` → `TodoListItem.vue`                             | `TodoList.vue` → `ListItem.vue` (unclear owner) |
| Component names go general → specific                       | `SearchInput.vue`, `SearchInputClearButton.vue`                 | `ClearButtonForSearch.vue`                      |
| Self-closing when no slot content (SFC/string templates)    | `<UserAvatar />`                                                | `<UserAvatar></UserAvatar>` (in SFC)            |
| PascalCase in SFC templates, kebab-case in in-DOM templates | SFC: `<UserProfile />`; in-DOM: `<user-profile></user-profile>` | kebab-case inside an SFC template               |
| Full words over abbreviations                               | `NavigationDrawer.vue`                                          | `NavDrwr.vue`                                   |
| Multiple attributes → one per line                          | each prop/directive on its own line when element has 2+ attrs   | all attributes crammed on one line              |

## Nuance — needs the shape, not just the rule

**Never `v-if` with `v-for` on the same element** — pre-filter with a computed property:

```vue
<script setup lang="ts">
const activeUsers = computed(() => users.value.filter((u) => u.isActive));
</script>
<template>
  <li v-for="user in activeUsers" :key="user.id">{{ user.name }}</li>
</template>
```

**Templates hold only simple expressions** — move logic into `computed`/methods:

```vue
<script setup lang="ts">
const normalizedFullName = computed(() =>
  `${props.firstName} ${props.lastName}`.trim().toUpperCase()
);
</script>
<template>
  <p>{{ normalizedFullName }}</p>
</template>
```

**Split complex computed properties into smaller named ones**, each one clear piece of derived state:

```vue
<script setup lang="ts">
const basePrice = computed(() => props.quantity * props.unitPrice);
const discount = computed(() => basePrice.value * props.discountRate);
const finalPrice = computed(() => basePrice.value - discount.value);
</script>
```
