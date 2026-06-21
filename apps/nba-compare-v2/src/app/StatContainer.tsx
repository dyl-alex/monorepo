import { Card, CardContent, CardHeader } from '@/components/ui/card'
import 'react'
import StatTable from './StatTable'

export default function StatContainer() {
    
    return(
    <div className='flex flex-row'>
        <div className='flex flex-col'>
        <img>
        
        </img>
        <Card>
            <CardHeader>
              Bio  
            </CardHeader>
            <CardContent>
                Height, (current) Age, Weight, ect from profile
            </CardContent>
        </Card>
        </div>
        <StatTable/>
    </div>
    )
}