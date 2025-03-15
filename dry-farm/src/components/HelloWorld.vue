<template>
  <div>
    <p>{{ msg }}</p>
  </div>
</template>

<script lang="ts">
import $axios from 'axios';

export default {
  name: 'Ping',
  data() {
    return {
      msg: '',
    };
  },
  created() {
    this.getMessage();
  },
  methods: {
    getMessage() {
      $axios.get('/')
        .then((res) => {
          this.msg = res.data;
        })
        .catch((error) => {
          console.error(error);
        });
    },
  },
};
</script>
