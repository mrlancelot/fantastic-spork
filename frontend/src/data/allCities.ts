import Fuse, { IFuseOptions } from 'fuse.js';
import citiesData from 'cities.json';
import { getStateName } from './stateNames';

export interface City {
  name: string;
  country: string;
  state?: string;
  displayName: string;
  population?: number;
  lat: number;
  lng: number;
}

// Transform and cache the cities data
let cities: City[] | null = null;
let fuseInstance: Fuse<City> | null = null;

// Function to get cities data
function getCities(): City[] {
  if (cities) return cities;
  
  // Transform the cities.json data to our format
  // Note: cities.json doesn't include population data
  // admin1 is typically state/province, admin2 is county/district
  cities = citiesData
    .map((city: any) => {
      // Get state/province name if available
      const stateCode = city.admin1;
      const stateName = stateCode ? getStateName(city.country, stateCode) : '';
      
      // Build display name with state if available
      let displayName = city.name;
      if (stateName && stateName.length > 0 && stateName !== city.name) {
        displayName += `, ${stateName}`;
      }
      displayName += `, ${city.country}`;
      
      return {
        name: city.name,
        country: city.country,
        state: stateName || undefined,
        displayName: displayName,
        population: undefined, // cities.json doesn't have population data
        lat: parseFloat(city.lat),
        lng: parseFloat(city.lng)
      };
    });
  
  console.log(`Loaded ${cities.length} cities for search`);
  return cities;
}

// Initialize Fuse.js instance
function initializeFuse(): Fuse<City> {
  if (fuseInstance) return fuseInstance;
  
  const citiesList = getCities();
  
  // Configure Fuse.js for optimal fuzzy search
  const fuseOptions: IFuseOptions<City> = {
    keys: [
      { name: 'name', weight: 0.7 },
      { name: 'country', weight: 0.3 }
    ],
    threshold: 0.4, // Allows for fuzzy matching
    includeScore: true,
    shouldSort: true,
    minMatchCharLength: 2,
    ignoreLocation: true, // Search entire string, not just beginning
    useExtendedSearch: false
  };
  
  fuseInstance = new Fuse(citiesList, fuseOptions);
  return fuseInstance;
}

// Search function that returns sorted results
export function searchCities(query: string, limit: number = 10): City[] {
  if (!query || query.length < 2) return [];
  
  const fuse = initializeFuse();
  
  // Perform fuzzy search
  const searchResults = fuse.search(query);
  
  // Sort by score (best matches first) and then by population (larger cities first)
  const sortedResults = searchResults
    .sort((a, b) => {
      // First sort by score (lower is better)
      const scoreDiff = (a.score || 0) - (b.score || 0);
      if (Math.abs(scoreDiff) > 0.05) return scoreDiff;
      
      // If scores are similar, sort by population (higher is better)
      const popA = a.item.population || 0;
      const popB = b.item.population || 0;
      return popB - popA;
    })
    .slice(0, limit)
    .map(result => result.item);
  
  return sortedResults;
}

// Function to check if a value is a valid city selection
export function isValidCity(value: string): boolean {
  const citiesList = getCities();
  return citiesList.some(city => city.displayName === value);
}

// Initialize cities data immediately
getCities();