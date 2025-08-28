import { createFileRoute } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import ReactMarkdown from 'react-markdown'

async function getAnalysis() {
  const rep = await fetch('http://127.0.0.1:8000/api/analysis')
  return rep.json()
}

export const Route = createFileRoute('/analysis')({
  component: App,
})

function App() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['email'],
    queryFn: getAnalysis,
  })
  // __AUTO_GENERATED_PRINT_VAR_START__
  console.log('App data:', data) // __AUTO_GENERATED_PRINT_VAR_END__

  if (isLoading) {
    return <div>Loading ....</div>
  }

  if (error) return 'error'

  if (!data) {
    return <div>No data available.</div>
  }

  const dataUrl = `data:image/jpeg;base64,${data}`

  return (
    <div className="flex justify-center mt-12">
      <img src={dataUrl} className="w-80 h-full" />
    </div>
  )
}
