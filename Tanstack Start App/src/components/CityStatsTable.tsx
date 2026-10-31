import {useMemo,useState} from 'react'
import {flexRender,getCoreRowModel,getSortedRowModel,useReactTable} from '@tanstack/react-table'
import type {ColumnDef,SortingState} from '@tanstack/react-table'
import type {Sport} from './types'
export interface CityStatsRow {label:string;runs:number;runMiles:number;rides:number;rideMiles:number}
export function CityStatsTable({rows,onSelect}:{rows:CityStatsRow[];onSelect:(label:string,sport:Sport)=>void}){
 const [sorting,setSorting]=useState<SortingState>([{id:'runs',desc:true}])
 const columns=useMemo<ColumnDef<CityStatsRow>[]>(()=>[
  {accessorKey:'label',header:'City',cell:({row})=><button className="city-name-button" title={row.original.label} onClick={()=>onSelect(row.original.label,row.original.runs?'runs':'bikes')}>{row.original.label}</button>},
  ...(['runs','rides'] as const).map(key=>({accessorKey:key,header:key==='runs'?'Runs':'Bike rides',sortDescFirst:true,cell:({row}:{row:{original:CityStatsRow}})=>{const city=row.original;return <button className="city-activity-button" disabled={!city[key]} aria-label={`View ${city.label} ${key==='runs'?'runs':'bike rides'}`} onClick={()=>onSelect(city.label,key==='runs'?'runs':'bikes')}><strong>{city[key].toLocaleString()}</strong><small>{(key==='runs'?city.runMiles:city.rideMiles).toLocaleString('en-US',{maximumFractionDigits:1})} mi</small></button>}}))
 ],[onSelect])
 const table=useReactTable({data:rows,columns,state:{sorting},onSortingChange:setSorting,getCoreRowModel:getCoreRowModel(),getSortedRowModel:getSortedRowModel(),enableSortingRemoval:false})
 return <div className="city-table-wrap" tabIndex={0} role="region" aria-label="Scrollable city statistics"><table className="city-table"><thead>{table.getHeaderGroups().map(group=><tr key={group.id}>{group.headers.map(header=><th key={header.id} scope="col" aria-sort={header.column.getIsSorted()==='asc'?'ascending':header.column.getIsSorted()==='desc'?'descending':'none'}><button onClick={header.column.getToggleSortingHandler()}>{flexRender(header.column.columnDef.header,header.getContext())}<span aria-hidden="true">{header.column.getIsSorted()==='asc'?' ↑':header.column.getIsSorted()==='desc'?' ↓':' ↕'}</span></button></th>)}</tr>)}</thead><tbody>{table.getRowModel().rows.map(row=><tr key={row.original.label}>{row.getVisibleCells().map((cell,i)=>i===0?<th scope="row" key={cell.id}>{flexRender(cell.column.columnDef.cell,cell.getContext())}</th>:<td key={cell.id}>{flexRender(cell.column.columnDef.cell,cell.getContext())}</td>)}</tr>)}</tbody></table></div>
}
