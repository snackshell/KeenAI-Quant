import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "@/components/ui/card"

export function CodePreviewCard() {
  return (
    <Card className="bg-[#0D0D0D] border-neutral-800 shadow-xl">
      <CardHeader className="flex flex-row items-center justify-between p-2 px-4 border-b border-neutral-800">
        <div className="flex items-center space-x-2">
          <div className="flex space-x-1.5">
            <span className="h-3 w-3 rounded-full bg-red-500"></span>
            <span className="h-3 w-3 rounded-full bg-yellow-500"></span>
            <span className="h-3 w-3 rounded-full bg-green-500"></span>
          </div>
          <div className="text-sm text-neutral-400">
            <span className="bg-neutral-800 px-3 py-1 rounded-md">auth.ts</span>
            <span className="ml-2">client.ts</span>
          </div>
        </div>

      </CardHeader>
      <CardContent className="p-4">
        <pre className="text-sm">
          <code className="language-typescript">
            <span className="text-gray-500">01 </span><span className="text-pink-400">export</span> <span className="text-cyan-400">const</span> <span className="text-white">auth</span> = <span className="text-yellow-400">betterAuth</span>(&#123;{'\n'}
            <span className="text-gray-500">02 </span>  <span className="text-white">database:</span> <span className="text-pink-400">new</span> <span className="text-yellow-400">Pool</span>(&#123;{'\n'}
            <span className="text-gray-500">03 </span>    <span className="text-white">connectionString:</span> <span className="text-purple-400">DATABASE_URL</span>,{'\n'}
            <span className="text-gray-500">04 </span>  &#125;),{'\n'}
            <span className="text-gray-500">05 </span>  <span className="text-white">emailAndPassword:</span> &#123;{'\n'}
            <span className="text-gray-500">06 </span>    <span className="text-white">enabled:</span> <span className="text-green-400">true</span>,{'\n'}
            <span className="text-gray-500">07 </span>  &#125;,{'\n'}
            <span className="text-gray-500">08 </span>  <span className="text-white">plugins:</span> [{'\n'}
            <span className="text-gray-500">09 </span>    <span className="text-yellow-400">organization</span>(),{'\n'}
            <span className="text-gray-500">10 </span>    <span className="text-yellow-400">twoFactor</span>(),{'\n'}
            <span className="text-gray-500">11 </span>  ]{'\n'}
            <span className="text-gray-500">12 </span>&#125;)
          </code>
        </pre>
      </CardContent>
      <CardFooter className="flex justify-end p-2 border-t border-neutral-800">
        <Button variant="link" className="text-neutral-400">Demo</Button>
      </CardFooter>
    </Card>
  )
}
