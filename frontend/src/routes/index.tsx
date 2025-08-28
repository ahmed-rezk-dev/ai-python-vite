import { createFileRoute } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import ReactMarkdown from 'react-markdown'

async function getfirstai() {
  const rep = await fetch('http://127.0.0.1:8000/api/firstai/html')
  return rep.json()
}

async function getEmail() {
  const rep = await fetch('http://127.0.0.1:8000/api/email')
  return rep.json()
}

export const Route = createFileRoute('/')({
  component: App,
})

function App() {
  // const { data, isLoading, error } = useQuery({
  //   queryKey: ['firstai'],
  //   queryFn: getfirstai,
  // })

  const {
    data,
    isLoading: isEmailLoading,
    error,
  } = useQuery({
    queryKey: ['email'],
    queryFn: getEmail,
  })

  if (isEmailLoading) {
    return <div>Loading ....</div>
  }

  if (error) return 'error'

  if (!data) {
    return <div>No data available.</div>
  }

  const dataUrl = `data:image/jpeg;base64,${data}`

  return (
    <div className="text-center">
      {/* <ReactMarkdown>{data}</ReactMarkdown> */}
      <img src={dataUrl} className="w-80 h-full object-cover" />
    </div>
  )
}
