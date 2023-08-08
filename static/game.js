class Game {
  constructor(state) {
    this.state = state
  }

  async init() {
    this.$board = $('#game-table')
    this.$timerscore = $('#timer-score-toast')
    this.$guessForm = $('#guess-form')
    this.$startBtn = $('#start-game-btn')
    this.bsTimerScoreToast = bootstrap.Toast.getOrCreateInstance(this.$timerscore.get(0), {autohide: false})
    this.$scoreBoardModal = $('#score-board-modal')
    this.bsScoreBoardModal = bootstrap.Modal.getOrCreateInstance('#score-board-modal')

    this.isTimeout = false
    this.hints = []
    await this.checkCurrentGame()
    if (this.state && this.calcTimeLeft() <= 0) {
      await this.onGameEnded()
      return
    }
    if (!this.state) return
    this.render()
    this._intervalId = setInterval(this.tick.bind(this), 1000)
    this.loadHints()
  }

  render() {
    this.$board.empty()

    if (!this.isStarted() || this.isEnded()) {
      this.$guessForm.attr('disabled', true)
      this.bsTimerScoreToast.hide()
      this.$startBtn.attr('disabled', false)
      if (this.isEnded()) {
        this.$scoreBoardModal.find('#highest-score').text(this.history['highscore'] )
        this.$scoreBoardModal.find('#current-score').text(this.currentScore)
        this.$scoreBoardModal.find('#number-of-plays').text(this.history['plays'])
        this.bsScoreBoardModal.show()
      }
      return
    }
    
    this.$startBtn.attr('disabled', true)
    this.$guessForm.attr('disabled', false)

    const {board, score} = this.state
    for (let row of board) {
      for (let cell of row) {
        this.$board.append(`<div class="cell">${cell}</div>`)
      }
    }
    this.$timerscore.find('#timer').text(this.calcTimeLeft())
    this.$timerscore.find('#score').text(score)
    this.bsTimerScoreToast.show()
  }

  isStarted() {
    return this.state !== null
  }

  isEnded() {
    return this.isTimeout
  }

  async onGameEnded() {
    this.isTimeout = true
    await this.end()
    this.render()
    this.reset()
  }

  reset() {
    this.isTimeout = false
    this.state = null
  }

  tick() {
    if (this.state === null) return 
    if (this.calcTimeLeft() <= 0) {
      clearInterval(this._intervalId)
      this.onGameEnded()
    }
    this.$timerscore.find('#timer').text(this.calcTimeLeft())
    this.$timerscore.find('#score').text(this.state['score'])
  }

  dispose() {
    if (this._intervalId) {
      clearInterval(this._intervalId)
    }
  }

  calcTimeLeft() {
    if (this.state === null) return 0
    const {timer} = this.state
    return Math.round(60 - ((Date.now() / 1000) - timer))
  }

  getSize() {
    if (!this.state) return 0
    return this.state['board'].length
  }

  xy2cell(x, y) {
    const size = this.getSize()
    return x * size + y
  }

  highlightCell(x, y, delay, duration, hsl = '45, 95%, 45%') {
    const nCell = this.xy2cell(x, y)
    const $cell = this.$board.children(`div:nth-child(${nCell+1})`)
    $cell.addClass('highlight')
    $cell.css('--delay', delay + 'ms')
    $cell.css('--duration', duration + 'ms')
    $cell.css('--color', hsl)
    setTimeout(() => $cell.removeClass('highlight'), 2000)
  }

  async checkCurrentGame() {
    try {
      const res = await axios.get('/current-game')
      const data = res.data
      this.state = data.state
    } catch (err){
      console.error(err)
    }
  }

  async start(size=5) {
    try {
      const res = await axios.post(`/start/${size}`)
      this.state = res.data
      this.render()
      this._intervalId = setInterval(this.tick.bind(this), 1000)
      this.loadHints()

    } catch (err) {
      if (err.response) throw err.response
      console.error(err)
    }
  }

  async guess(word) {
    if (!this.isStarted()) return
    try {
      const res = await axios.post(`/guess/${word}`)
      const data = res.data
      if (data['found']) {
        this.state['score'] = data['score']
        this.state['found_words'].push(word.toUpperCase())
        return data['found']
      }
      return data['status']
    } catch (err) {
      console.error(err)
      return null
    }
  }

  async end() {
    if (!this.isStarted()) return
    try {
      const res = await axios.post('/end')
      this.history = res.data.history
      this.currentScore = this.state['score']
      this.state = null
      return res.data
    } catch (err) {
      console.error(err)
    }
  }

  async loadHints() {
    try {
      const res = await axios.get('/hint')
      this.hints = res.data.hints
        .filter(hint => hint.length > 1)
        .sort((a, b) => b.length - a.length)
    } catch(err) {
      console.error(err)
      this.hints = []
    }
  }

  async getHint() {
    const getWord = (seq, board) => {
      let word = ''
      for (let [y, x] of seq) {
        word += board[y][x]
      }
      return word
    }
    const hints = this.hints.filter(
      hint => 
        !this.state['found_words'].includes(getWord(hint, this.state['board'])))
    return hints[0]
  }
}