
$(() => {
  /** @type {JQuery<HTMLFormElement>} */
  const $guessForm = $('#guess-form')
  const $guessInput = $('#guess-form input[type="text"]')
  const $startGameBtn = $('#start-game-btn')
  const $hintBtn = $('#hint-btn')

  const toast = new Toast()
  const game = new Game()

  toast.mountToUI()
  game.init()

  $guessForm.on('submit', onGuessSubmit)
  $startGameBtn.on('click', onStartGameClicked)
  $hintBtn.on('click', onHintClicked)

  /** @type {JQuery.EventHandler<HTMLFormElement, typeof $guessForm>} */
  async function onGuessSubmit(evt) {
    evt.preventDefault()
    const word = $guessInput.val()
    $guessForm.get(0).reset()
    const data = await game.guess(word)
    if (Array.isArray(data)) {
      let idx = 0
      for (let [x, y] of data) {
        game.highlightCell(x, y, idx * 200, 2000 + (data.length - idx) * 200)
        idx++
      }
    }
  }

  async function onStartGameClicked() {
    game.start()
  }

  async function onHintClicked() {
    $hintBtn.attr('disabled', true)
    const hint = await game.getHint()
    let idx = 0
    for (let [y, x] of hint) {
      game.highlightCell(y, x, idx * 200, 500 + (hint.length - idx) * 50, '3, 63%, 45%')
      idx++
    }
    setTimeout(() => $hintBtn.attr('disabled', false), hint.length * 250 + 500)
  }
})