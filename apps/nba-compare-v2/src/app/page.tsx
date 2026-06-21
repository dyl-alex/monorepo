import { Card, CardContent, CardDescription, CardHeader } from "@/components/ui/card";
import StatContainer from "./StatContainer";
import { ChartBar } from "lucide-react";
import { Input } from "@/components/ui/input";

export default function Home() {
  return (
    <div className="flex flex-col">
      <Card className="w-full mx-auto max-w-sm">
        <CardHeader>
          Welcome to NBA Compare
        </CardHeader>
        <CardDescription>
          Please enter in a players name below to view basic statistics.
        </CardDescription>
        <CardContent>
          <Input/>
          <StatContainer/>
        </CardContent>
      </Card>

      <Card className="w-full mx-auto max-w-sm">
        <CardHeader>
          Chart view
        </CardHeader>
        <CardContent>
          <ChartBar>

          </ChartBar>
        </CardContent>
      </Card>
    </div>
  );
}
