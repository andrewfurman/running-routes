/** Display/group labels use a consistent place, state-or-country format. */
const labels:Record<string,string>={
 'Mainline Pennsylvania':'Mainline, PA','San Francisco Bay Area':'SF Bay, CA','Chicago / Milwaukee':'Chicago Area, IL','Chicago area, IL':'Chicago Area, IL','Cancún / Riviera Maya':'Cancun, MX','New Orleans / Louisiana':'New Orleans, LA',
 'Allentown, PA':'Allentown Greater Area, PA','Center Valley, PA':'Allentown Greater Area, PA','Coopersburg, PA':'Allentown Greater Area, PA',
 'Paoli, PA':'Mainline, PA','Wayne, PA':'Outer Philly Suburbs, PA','King of Prussia, PA':'Outer Philly Suburbs, PA','Village Green-Green Ridge, PA':'Outer Philly Suburbs, PA',
 'Maple Glen, PA':'Outer Philly Suburbs, PA','Horsham, PA':'Outer Philly Suburbs, PA','Willow Grove, PA':'Outer Philly Suburbs, PA','West Conshohocken, PA':'Outer Philly Suburbs, PA','outer Philly suburbs':'Outer Philly Suburbs, PA','Wilton, CT':'Ridgefield, CT',
 'Seattle':'Seattle, WA','Fargo':'Fargo, ND','Indianapolis':'Indianapolis, IN','St. Louis':'St. Louis, MO','Minneapolis':'Minneapolis, MN','Charleston':'Charleston, SC','Savannah':'Savannah, GA','Portland':'Portland, OR','Boise':'Boise, ID','San Diego':'San Diego, CA','Lake Tahoe':'Lake Tahoe, CA/NV',
 'London':'London, UK','Milan':'Milan, IT','Berlin':'Berlin, DE','Japan':'Japan, JP','South Korea':'South Korea, KR','Seychelles':'Seychelles, SC','Grand Cayman':'Grand Cayman, KY','Victoria, Canada':'Victoria, BC','Atlantic Ocean':'Atlantic Ocean, US',
 'Boston / New England':'New England, US','Other Havertown / Philadelphia area':'Other Philly Area, PA','Other New York / New Jersey area':'NY/NJ Area, US'
}
export function cityLabel(label:string){return labels[label]||label}
