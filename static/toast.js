class Toast {
  constructor() {
    this.$container = jQuery(`<div id="toast-container" class="toast-container position-fixed top-0 end-0" aria-live="polite" aria-atomic="true"></div>`)
  }

  mountToUI() {
    this.$container.appendTo(document.body)
  }
  unMountFromUI() {
    $(document.body).remove('#toast-container')
  }

  makeToast(message) {
    const $toast = $(`<div class="toast" role="alert" aria-live="assertive" aria-atomic="true">
    <div class="toast-header">
      <i class="me-2 ratio-1x1 bg-success rounded-5 " style="width:20px; height: 20px;"></i>
      <strong class="me-auto">Notification</strong>
      <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>
    <div class="toast-body">
      ${message}
    </div>
  </div>`)
    this.$container.append($toast)
    $toast.on('hidden.bs.toast', () => { $toast.remove() })
    const bsToast = bootstrap.Toast.getOrCreateInstance($toast, {autohide: false})
    bsToast.show()
  }
}