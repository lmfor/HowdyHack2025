export class DatabaseQueue {
  static _instance = null
  _locked = false
  _waiting = []

  static instance() {
    if (!this._instance) this._instance = new DatabaseQueue()
    return this._instance
  }

  async run(fn) {
    await this._acquire()
    try {
      return await fn()
    } finally {
      this._release()
    }
  }

  _acquire() {
    if (!this._locked) {
      this._locked = true
      return Promise.resolve()
    }
    return new Promise((resolve) => {
      this._waiting.push(() => {
        this._locked = true
        resolve()
      })
    })
  }

  _release() {
    const next = this._waiting.shift()
    if (next) queueMicrotask(next)
    else this._locked = false
  }
}