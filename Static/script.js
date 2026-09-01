document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll('input[type="file"]').forEach(input => {
    input.addEventListener("change", () => {
      const label = input.closest(".dropzone");
      if (input.files.length) {
        label.querySelector("small").textContent = input.files[0].name;
      }
    });
  });
});
