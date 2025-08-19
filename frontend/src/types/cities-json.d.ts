declare module 'cities.json' {
  interface City {
    name: string;
    country: string;
    lat: string;
    lng: string;
    population?: number;
    admin1?: string;
    admin2?: string;
  }
  
  const cities: City[];
  export default cities;
}