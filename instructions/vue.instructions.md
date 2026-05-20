---
description: Vue Code Standards.
applyTo: "**/*.vue"
---

# Vue Code Standards

## All Code Must Be Written in English

All component names, variable names, function names, prop names, comments, and template content must be written in English.

```vue
// ✅ Good
<script setup lang="ts">
const isUserLoggedIn = ref(false);
function handleSubmit() {}
</script>

// ❌ Bad
<script setup lang="ts">
const estaLogado = ref(false);
function enviarFormulario() {}
</script>
```

---

## Use Multi-Word Component Names

Component names should always be multi-word to avoid conflicts with existing and future HTML elements, which are always single-word.

```vue
// ✅ Good
<!-- UserProfile.vue -->
<script setup lang="ts">
// Component: UserProfile
</script>

// ❌ Bad
<!-- Profile.vue -->
<script setup lang="ts">
// Component: Profile  — conflicts with potential HTML element
</script>
```

---

## Use Detailed Prop Definitions

Props should always be defined with their type, required status, and a validator or default value when applicable. Avoid using shorthand array syntax for props in production code.

```vue
// ✅ Good
<script setup lang="ts">
interface Props {
  status: "active" | "inactive" | "pending";
  userId: number;
  label?: string;
}

const props = withDefaults(defineProps<Props>(), {
  label: "Default Label"
});
</script>

// ❌ Bad
<script setup lang="ts">
const props = defineProps(["status", "userId", "label"]);
</script>
```

---

## Use Keyed `v-for`

Always provide a unique `:key` attribute when using `v-for`. Never use the loop index as the key when iterating over data that can be reordered or filtered.

```vue
// ✅ Good
<template>
  <ul>
    <li v-for="user in users" :key="user.id">
      {{ user.name }}
    </li>
  </ul>
</template>

// ❌ Bad
<template>
  <ul>
    <li v-for="(user, index) in users" :key="index">
      {{ user.name }}
    </li>
  </ul>
</template>
```

---

## Avoid `v-if` with `v-for`

Never use `v-if` and `v-for` on the same element. Move the condition to a wrapping element or use a computed property to pre-filter the list.

```vue
// ✅ Good — filter with computed property
<script setup lang="ts">
const activeUsers = computed(() => users.value.filter((u) => u.isActive));
</script>

<template>
  <ul>
    <li v-for="user in activeUsers" :key="user.id">
      {{ user.name }}
    </li>
  </ul>
</template>

// ❌ Bad
<template>
  <ul>
    <li v-for="user in users" v-if="user.isActive" :key="user.id">
      {{ user.name }}
    </li>
  </ul>
</template>
```

---

## Use Component-Scoped Styling

Always add the `scoped` attribute to `<style>` blocks to prevent styles from leaking into other components.

```vue
// ✅ Good
<style scoped>
.card {
  border-radius: 8px;
  padding: 16px;
}
</style>

// ❌ Bad
<style>
.card {
  border-radius: 8px;
  padding: 16px;
}
</style>
```

---

## Each Component Should Be in Its Own File

Every component must reside in its own `.vue` Single-File Component (SFC) file. Do not define multiple components in a single file.

```
// ✅ Good
components/
  UserCard.vue
  UserAvatar.vue
  UserBadge.vue

// ❌ Bad
components/
  UserComponents.vue  // defines UserCard, UserAvatar, UserBadge all in one file
```

---

## Filenames of SFCs Should Be Consistently PascalCase or kebab-case

Pick one naming convention for SFC filenames and apply it consistently across the entire project. PascalCase is preferred in most setups.

```
// ✅ Good — consistently PascalCase
UserCard.vue
UserProfile.vue
BaseButton.vue

// ✅ Good — consistently kebab-case
user-card.vue
user-profile.vue
base-button.vue

// ❌ Bad — mixed conventions
UserCard.vue
user-profile.vue
BaseButton.vue
```

---

## Base Components Should Have a Consistent Prefix

Presentational/dumb/pure components that apply app-specific styling and conventions should use a consistent prefix such as `Base`, `App`, or `V`.

```
// ✅ Good
BaseButton.vue
BaseInput.vue
BaseCard.vue
BaseModal.vue

// ❌ Bad
Button.vue        // too generic, no prefix
MyButton.vue      // inconsistent prefix
CustomInput.vue   // inconsistent prefix
```

---

## Child Components Should Include the Parent Name as a Prefix

Components tightly coupled to a specific parent should include the parent component name as a prefix to make their relationship explicit in the file tree.

```
// ✅ Good
TodoList.vue
TodoListItem.vue
TodoListItemActions.vue

// ❌ Bad
TodoList.vue
ListItem.vue      // unclear which list
ItemActions.vue   // unclear which item or list
```

---

## Component Names Should Go from General to Specific

Name components starting with the highest-level (most general) concept and ending with descriptive modifiers. This groups related components together alphabetically.

```
// ✅ Good
SearchInput.vue
SearchInputClearButton.vue
SearchInputSuggestions.vue

// ❌ Bad
ClearButtonForSearch.vue
InputSearch.vue
SuggestionsForSearch.vue
```

---

## Self-Closing Components When There Is No Content

Components with no slot content should be self-closing in SFCs, string templates, and JSX. In in-DOM templates, always use the explicit closing tag.

```vue
// ✅ Good — SFC or string template
<template>
  <UserAvatar />
  <BaseButton label="Submit" />
</template>

// ✅ Good — in-DOM template (index.html)
<user-avatar></user-avatar>
<base-button label="Submit"></base-button>

// ❌ Bad — SFC
<template>
  <UserAvatar></UserAvatar>
</template>
```

---

## PascalCase in SFCs, kebab-case in In-DOM Templates

Use PascalCase component names in Single-File Components and string templates. Use kebab-case when writing components directly in HTML (in-DOM templates).

```vue
// ✅ Good — inside a .vue SFC template
<template>
  <UserProfile :user="currentUser" />
  <BaseButton label="Save" />
</template>

// ✅ Good — in-DOM template (plain HTML)
<div id="app">
  <user-profile :user="currentUser"></user-profile>
  <base-button label="Save"></base-button>
</div>

// ❌ Bad — kebab-case inside SFC template
<template>
  <user-profile :user="currentUser" />
</template>
```

---

## Component Names Should Prefer Full Words Over Abbreviations

Avoid abbreviations in component names. Clarity and readability are more important than saving a few keystrokes.

```
// ✅ Good
UserProfileAvatar.vue
NavigationDrawer.vue
SettingsCheckbox.vue

// ❌ Bad
UsrProfAvtr.vue
NavDrwr.vue
SttngsChkbx.vue
```

---

## Elements with Multiple Attributes Should Span Multiple Lines

When an element has more than one attribute, place each attribute on its own line for readability.

```vue
// ✅ Good
<template>
  <BaseInput
    v-model="searchQuery"
    type="text"
    placeholder="Search..."
    :disabled="isLoading"
    @keyup.enter="handleSearch"
  />
</template>

// ❌ Bad
<template>
  <BaseInput
    v-model="searchQuery"
    type="text"
    placeholder="Search..."
    :disabled="isLoading"
    @keyup.enter="handleSearch"
  />
</template>
```

---

## Templates Should Only Include Simple Expressions

Component templates should contain only simple expressions. Move complex logic into computed properties or methods to keep templates readable and testable.

```vue
// ✅ Good
<script setup lang="ts">
const normalizedFullName = computed(() =>
  `${props.firstName} ${props.lastName}`.trim().toUpperCase()
);
</script>

<template>
  <p>{{ normalizedFullName }}</p>
</template>

// ❌ Bad
<template>
  <p>{{ `${firstName} ${lastName}`.trim().toUpperCase() }}</p>
</template>
```

---

## Split Complex Computed Properties into Simpler Ones

Break a large computed property into multiple smaller, named computed properties. Each should represent one clear piece of derived state.

```vue
// ✅ Good
<script setup lang="ts">
const basePrice = computed(() => props.quantity * props.unitPrice);
const discount = computed(() => basePrice.value * props.discountRate);
const finalPrice = computed(() => basePrice.value - discount.value);
</script>

// ❌ Bad
<script setup lang="ts">
const finalPrice = computed(
  () =>
    props.quantity * props.unitPrice -
    props.quantity * props.unitPrice * props.discountRate
);
</script>
```
