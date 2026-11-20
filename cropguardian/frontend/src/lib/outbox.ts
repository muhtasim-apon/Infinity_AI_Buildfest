/**
 * Offline outbox (Gantt P3 step 2): photos taken without a network wait in IndexedDB and are sent
 * when the device is back online, with the SAME Idempotency-Key, so a retry never makes a second
 * scan. State machine per item: queued -> sending -> (sent: removed) | (failed: back to queued).
 * Storage can be unavailable (private mode): every call fails soft and the UI says so.
 */

export interface OutboxItem {
  key: string // the Idempotency-Key, also the IndexedDB key
  region: string
  blob: Blob
  createdAt: number
}

const DB = 'cg-outbox'
const STORE = 'photos'
const MAX_ITEMS = 20

function open(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    if (typeof indexedDB === 'undefined') {
      reject(new Error('no-indexeddb'))
      return
    }
    const req = indexedDB.open(DB, 1)
    req.onupgradeneeded = () => req.result.createObjectStore(STORE, { keyPath: 'key' })
    req.onsuccess = () => resolve(req.result)
    req.onerror = () => reject(req.error ?? new Error('idb-open'))
  })
}

function tx<T>(
  mode: IDBTransactionMode,
  run: (store: IDBObjectStore) => IDBRequest<T>,
): Promise<T> {
  return open().then(
    (db) =>
      new Promise<T>((resolve, reject) => {
        const t = db.transaction(STORE, mode)
        const req = run(t.objectStore(STORE))
        req.onsuccess = () => resolve(req.result)
        req.onerror = () => reject(req.error ?? new Error('idb-request'))
        t.oncomplete = () => db.close()
      }),
  )
}

export const outbox = {
  async list(): Promise<OutboxItem[]> {
    try {
      const items = await tx<OutboxItem[]>(
        'readonly',
        (s) => s.getAll() as IDBRequest<OutboxItem[]>,
      )
      return items.sort((a, b) => a.createdAt - b.createdAt)
    } catch {
      return []
    }
  },
  async add(item: OutboxItem): Promise<boolean> {
    try {
      if ((await this.list()).length >= MAX_ITEMS) return false
      await tx('readwrite', (s) => s.put(item))
      return true
    } catch {
      return false
    }
  },
  async remove(key: string): Promise<void> {
    try {
      await tx('readwrite', (s) => s.delete(key))
    } catch {
      // nothing to do: the next sync will try again and the server dedupes by key
    }
  },
}

/** Send every queued photo once. Returns how many were sent. Stops at the first network failure. */
export async function flushOutbox(
  send: (item: OutboxItem) => Promise<unknown>,
  isNetworkError: (err: unknown) => boolean,
): Promise<number> {
  let sent = 0
  for (const item of await outbox.list()) {
    try {
      await send(item)
      await outbox.remove(item.key)
      sent += 1
    } catch (err) {
      if (isNetworkError(err)) break // still offline: keep the rest queued
      await outbox.remove(item.key) // server rejected it (bad file): retrying would never succeed
    }
  }
  return sent
}
