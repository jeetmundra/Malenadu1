import { useEffect, useState } from 'react'

export function useSensorStream(machineId) {
  const [data, setData] = useState(null)

  useEffect(() => {
    // In dev, the FastAPI will be on localhost:8000
    // Make sure to set up proxy in next.config.mjs or cross-origin headers in FastAPI.
    // Assuming backend is at http://localhost:8000
    const es = new EventSource(`http://localhost:8000/stream/${machineId}`)
    
    es.onmessage = (e) => {
        try {
            setData(JSON.parse(e.data))
        } catch (err) {
            console.error("Failed to parse SSE data", err)
        }
    }

    es.onerror = (e) => {
        console.error("SSE Error for " + machineId, e)
    }

    return () => es.close()
  }, [machineId])

  return data
}
