;(function () {
  htmx.on("showMessage", (e) => {
      Swal.fire({
          html: `
              <div class="mt-3">
                  <lord-icon src="https://cdn.lordicon.com/lupuorrc.json" 
                      trigger="loop" 
                      colors="primary:#0ab39c,secondary:#405189" 
                      style="width:120px;height:120px">
                  </lord-icon>
                  <div class="mt-4 pt-2 fs-15">
                      <h4>Congratulations!</h4>
                      <p class="text-muted mx-4 mb-0">${e.detail.value}</p>
                  </div>
              </div>
          `,
          showCancelButton: true,
          showConfirmButton: false,
          cancelButtonClass: "btn btn-primary w-xs mb-1",
          cancelButtonText: "Back",
          buttonsStyling: false,
          showCloseButton: true
      });
  });
})();
