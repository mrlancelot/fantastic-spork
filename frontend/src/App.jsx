import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Plus,
  Clock,
  Star,
  Map,
  ExternalLink,
  Heart,
  Share,
  Download,
  Bell,
  CreditCard,
  LogOut,
  Sparkles,
  TrendingUp,
  Globe,
  Shield,
  Users
} from 'lucide-react';
import { SignedIn, SignedOut, UserButton, useUser, useClerk } from "@clerk/clerk-react";
import { useQuery, useMutation, useAction } from "convex/react";
import { api } from "../convex/_generated/api";
import { AuthWrapper } from "./components/AuthWrapper";
import { ConvexDebug } from "./components/ConvexDebug";
import { SignInPage } from "./components/SignInPage";
import { SignUpPage } from "./components/SignUpPage";
import { TripForm } from "./components/TripForm";

// Import all our new UI components
import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  Badge,
  HeroSection,
  DestinationCard,
  SearchBar,
  ChatInterface,
  NavBar,
  FeatureSection,
  Toast
} from './components/ui';

// Sample destination data
const popularDestinations = [
  {
    id: 1,
    destination: 'Tokyo, Japan',
    image: 'https://images.pexels.com/photos/2506923/pexels-photo-2506923.jpeg?auto=compress&cs=tinysrgb&w=800',
    rating: 4.8,
    price: 150,
    duration: 7,
    travelers: 2,
    tags: ['Culture', 'Food', 'Technology']
  },
  {
    id: 2,
    destination: 'Bali, Indonesia',
    image: 'https://images.pexels.com/photos/2166559/pexels-photo-2166559.jpeg?auto=compress&cs=tinysrgb&w=800',
    rating: 4.9,
    price: 80,
    duration: 10,
    travelers: 2,
    tags: ['Beach', 'Nature', 'Wellness']
  },
  {
    id: 3,
    destination: 'Paris, France',
    image: 'https://images.pexels.com/photos/338515/pexels-photo-338515.jpeg?auto=compress&cs=tinysrgb&w=800',
    rating: 4.7,
    price: 200,
    duration: 5,
    travelers: 2,
    tags: ['Romance', 'Art', 'History']
  },
  {
    id: 4,
    destination: 'New York, USA',
    image: 'https://images.pexels.com/photos/466685/pexels-photo-466685.jpeg?auto=compress&cs=tinysrgb&w=800',
    rating: 4.6,
    price: 250,
    duration: 4,
    travelers: 2,
    tags: ['Urban', 'Culture', 'Shopping']
  },
  {
    id: 5,
    destination: 'Dubai, UAE',
    image: 'https://images.pexels.com/photos/1534411/pexels-photo-1534411.jpeg?auto=compress&cs=tinysrgb&w=800',
    rating: 4.7,
    price: 300,
    duration: 6,
    travelers: 2,
    tags: ['Luxury', 'Modern', 'Shopping']
  },
  {
    id: 6,
    destination: 'Santorini, Greece',
    image: 'https://images.pexels.com/photos/1010657/pexels-photo-1010657.jpeg?auto=compress&cs=tinysrgb&w=800',
    rating: 4.9,
    price: 180,
    duration: 7,
    travelers: 2,
    tags: ['Island', 'Romance', 'Beach']
  }
];

function App() {
  const [currentScreen, setCurrentScreen] = useState('home');
  const [userIntent, setUserIntent] = useState(null);
  const [showToast, setShowToast] = useState(false);
  const { user, isSignedIn } = useUser();
  const { signOut } = useClerk();
  const currentUser = useQuery(api.users.getMyUser);
  const userTrips = useQuery(api.trips.getUserTrips);
  const sendChatMessage = useAction(api.chats.sendMessage);
  
  const trips = userTrips || [];
  
  // Handle SSO callback and user intent after authentication
  useEffect(() => {
    const hash = window.location.hash;
    if (hash.includes('/sso-callback')) {
      window.location.hash = '';
      setCurrentScreen('home');
    }
    
    // Handle user intent after successful authentication
    if (isSignedIn && userIntent) {
      const { action, data } = userIntent;
      switch (action) {
        case 'planning':
          setCurrentScreen('planning');
          // If there's search data, you could pass it to the planning screen
          break;
        case 'destination':
          setCurrentScreen('planning');
          break;
        case 'dashboard':
          setCurrentScreen('dashboard');
          break;
        default:
          setCurrentScreen(action);
      }
      setUserIntent(null); // Clear intent after handling
    }
  }, [isSignedIn, userIntent]);

  // Function to handle authenticated actions
  const handleAuthenticatedAction = (action, data = null) => {
    if (isSignedIn) {
      // User is authenticated, proceed with action
      switch (action) {
        case 'planning':
          setCurrentScreen('planning');
          break;
        case 'dashboard':
          setCurrentScreen('dashboard');
          break;
        default:
          setCurrentScreen(action);
      }
    } else {
      // Store intent and redirect to auth
      setUserIntent({ action, data });
      setShowToast(true);
      // Small delay to show toast before navigation
      setTimeout(() => {
        setCurrentScreen('signin');
      }, 500);
    }
  };

  // Page transition variants
  const pageVariants = {
    initial: { opacity: 0, x: -20 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: 20 }
  };

  const Homepage = () => (
    <motion.div
      initial="initial"
      animate="animate"
      exit="exit"
      variants={pageVariants}
      className="min-h-screen"
    >
      {/* Hero Section */}
      <HeroSection
        title="Plan Your Perfect Trip"
        subtitle="AI-powered travel planning with personalized itineraries that adapt to your style"
        ctaText="Start Planning with AI"
        onCtaClick={() => handleAuthenticatedAction('planning')}
        className="min-h-[600px]"
      />

      {/* Search Section */}
      <div className="py-20 px-4 bg-neutral-50">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Where would you like to go?
            </h2>
            <p className="text-xl text-neutral-600">
              Search destinations and let AI create your perfect itinerary
            </p>
          </motion.div>

          <SearchBar
            onSearch={(data) => {
              console.log('Search:', data);
              handleAuthenticatedAction('planning', data);
            }}
          />
        </div>
      </div>

      {/* Popular Destinations */}
      <div className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              <span className="gradient-text">Popular Destinations</span>
            </h2>
            <p className="text-xl text-neutral-600">
              Explore trending destinations handpicked by our AI
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {popularDestinations.map((dest, index) => (
              <motion.div
                key={dest.id}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <DestinationCard
                  {...dest}
                  onSelect={() => {
                    console.log('Selected:', dest.destination);
                    handleAuthenticatedAction('planning', { destination: dest.destination });
                  }}
                />
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Features Section */}
      <FeatureSection className="bg-neutral-50" />

      {/* Stats Section */}
      <div className="py-20 px-4 bg-gradient-to-br from-primary-600 to-secondary-600 text-white">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
            {[
              { label: 'Happy Travelers', value: '50K+', icon: Heart },
              { label: 'Destinations', value: '200+', icon: Globe },
              { label: 'AI Itineraries', value: '100K+', icon: Sparkles },
              { label: 'Trust Score', value: '4.9/5', icon: Shield }
            ].map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.5 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className="space-y-2"
              >
                <stat.icon className="w-12 h-12 mx-auto mb-4 opacity-80" />
                <div className="text-4xl font-bold">{stat.value}</div>
                <div className="text-white/80">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );

  const Dashboard = () => {
    const [showTripForm, setShowTripForm] = useState(false);

    return (
      <motion.div
        initial="initial"
        animate="animate"
        exit="exit"
        variants={pageVariants}
        className="min-h-screen bg-neutral-50 py-8"
      >
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-neutral-900 mb-2">My Trips</h1>
              <p className="text-neutral-600">Manage and view all your travel plans</p>
            </div>
            <Button 
              onClick={() => setShowTripForm(true)}
              size="lg"
              variant="gradient"
              className="shadow-lg"
            >
              <Plus className="w-5 h-5 mr-2" />
              New Trip
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {trips.length === 0 ? (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="col-span-full"
              >
                <Card className="text-center py-16">
                  <CardContent>
                    <div className="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-6">
                      <Map className="w-10 h-10 text-primary-600" />
                    </div>
                    <h3 className="text-2xl font-semibold text-neutral-900 mb-2">No trips yet</h3>
                    <p className="text-neutral-600 mb-6 max-w-sm mx-auto">
                      Start planning your next adventure with our AI-powered travel assistant
                    </p>
                    <Button
                      onClick={() => setShowTripForm(true)}
                      variant="primary"
                      size="lg"
                    >
                      Create Your First Trip
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>
            ) : (
              trips.map((trip, index) => {
                const startDate = new Date(trip.startDate);
                const endDate = new Date(trip.endDate);
                const today = new Date();
                const status = startDate > today ? 'upcoming' : endDate < today ? 'past' : 'ongoing';
                
                return (
                  <motion.div
                    key={trip._id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <Card className="h-full hover:shadow-2xl transition-shadow">
                      <div className="h-48 bg-gradient-to-br from-primary-400 to-primary-600 relative overflow-hidden">
                        <div className="absolute inset-0 bg-black/20" />
                        <div className="absolute inset-0 flex items-center justify-center">
                          <Map className="w-20 h-20 text-white/50" />
                        </div>
                        <Badge
                          variant={status === 'upcoming' ? 'success' : status === 'past' ? 'secondary' : 'primary'}
                          className="absolute top-4 right-4"
                        >
                          {status === 'upcoming' ? 'Upcoming' : status === 'past' ? 'Completed' : 'Ongoing'}
                        </Badge>
                      </div>
                      <CardContent className="pt-6">
                        <CardTitle className="mb-2">{trip.destination}</CardTitle>
                        <CardDescription className="mb-4">
                          {new Date(trip.startDate).toLocaleDateString()} - {new Date(trip.endDate).toLocaleDateString()}
                        </CardDescription>
                        <div className="flex items-center text-sm text-neutral-600 mb-6">
                          <Users className="w-4 h-4 mr-1" />
                          {trip.travelers} travelers
                        </div>
                        <div className="flex gap-2">
                          <Button 
                            onClick={() => setCurrentScreen('itinerary')}
                            variant="primary"
                            size="sm"
                            className="flex-1"
                          >
                            View Details
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            className="flex-1"
                          >
                            Edit Trip
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                );
              })
            )}
          </div>

          {showTripForm && (
            <TripForm 
              onClose={() => setShowTripForm(false)} 
              onSuccess={() => {
                setShowTripForm(false);
              }}
            />
          )}
        </div>
      </motion.div>
    );
  };

  const PlanningInterface = () => {
    return (
      <motion.div
        initial="initial"
        animate="animate"
        exit="exit"
        variants={pageVariants}
        className="min-h-screen bg-neutral-50 py-8"
      >
        <div className="max-w-7xl mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            <h1 className="text-4xl font-bold mb-4">
              <span className="gradient-text">AI Trip Planning</span>
            </h1>
            <p className="text-xl text-neutral-600">
              Chat with our AI to create your perfect itinerary
            </p>
          </motion.div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Trip Preferences */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
            >
              <Card className="h-full">
                <CardHeader>
                  <CardTitle>Trip Preferences</CardTitle>
                  <CardDescription>Tell us about your ideal trip</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 mb-2">Trip Type</label>
                    <div className="grid grid-cols-2 gap-3">
                      {['Adventure', 'Relaxation', 'Culture', 'Business'].map(type => (
                        <Button
                          key={type}
                          variant="outline"
                          className="justify-start"
                        >
                          {type}
                        </Button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-neutral-700 mb-2">Budget Range</label>
                    <select className="w-full px-4 py-3 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent">
                      <option>Budget ($50-100/day)</option>
                      <option>Mid-range ($100-200/day)</option>
                      <option>Luxury ($200+/day)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-neutral-700 mb-2">Interests</label>
                    <div className="flex flex-wrap gap-2">
                      {['Food', 'Museums', 'Nightlife', 'Nature', 'Shopping', 'History'].map(interest => (
                        <Badge
                          key={interest}
                          variant="outline"
                          className="cursor-pointer hover:bg-primary-50"
                        >
                          {interest}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <Button 
                    onClick={() => setCurrentScreen('itinerary')}
                    variant="gradient"
                    size="lg"
                    className="w-full"
                  >
                    Generate AI Itinerary
                  </Button>
                </CardContent>
              </Card>
            </motion.div>

            {/* AI Chat */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className="h-[600px]"
            >
              <ChatInterface
                onSendMessage={async (message) => {
                  try {
                    const response = await sendChatMessage({ message });
                    return response;
                  } catch (error) {
                    console.error('Error:', error);
                    return "Sorry, I encountered an error. Please try again.";
                  }
                }}
              />
            </motion.div>
          </div>
        </div>
      </motion.div>
    );
  };

  const ItineraryView = () => (
    <motion.div
      initial="initial"
      animate="animate"
      exit="exit"
      variants={pageVariants}
      className="min-h-screen bg-neutral-50 py-8"
    >
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-neutral-900">Tokyo Adventure</h1>
            <p className="text-neutral-600">March 15-22, 2024 • 2 travelers</p>
          </div>
          <div className="flex gap-3">
            <Button variant="outline" size="sm">
              <Share className="w-4 h-4 mr-2" />
              Share
            </Button>
            <Button variant="outline" size="sm">
              <Download className="w-4 h-4 mr-2" />
              Export
            </Button>
            <Button variant="primary" size="sm">
              <Heart className="w-4 h-4 mr-2" />
              Save
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            {/* Day 1 */}
            <Card>
              <CardHeader>
                <CardTitle>Day 1 - March 15</CardTitle>
                <CardDescription>Arrival and Exploration</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {[
                  { time: '08:00', title: 'Flight to Tokyo', location: 'JFK Airport', icon: '✈️' },
                  { time: '14:30', title: 'Hotel Check-in', location: 'Shibuya District', icon: '🏨' },
                  { time: '18:00', title: 'Ramen Dinner', location: 'Ichiran Shibuya', icon: '🍜' }
                ].map((item, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-start gap-4 p-4 rounded-lg border border-neutral-200 hover:shadow-md transition-all"
                  >
                    <div className="text-2xl">{item.icon}</div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <h4 className="font-semibold text-neutral-900">{item.title}</h4>
                        <span className="text-sm text-primary-600 font-medium">{item.time}</span>
                      </div>
                      <p className="text-sm text-neutral-600">{item.location}</p>
                    </div>
                    <Button variant="ghost" size="sm">
                      <ExternalLink className="w-4 h-4" />
                    </Button>
                  </motion.div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Trip Overview</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-neutral-600">Duration</span>
                  <span className="font-medium">7 days</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-neutral-600">Travelers</span>
                  <span className="font-medium">2 people</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-neutral-600">Budget</span>
                  <span className="font-medium">$2,400</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-neutral-600">Activities</span>
                  <span className="font-medium">12 planned</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button variant="primary" size="sm" className="w-full">
                  Book All Activities
                </Button>
                <Button variant="outline" size="sm" className="w-full">
                  Modify Itinerary
                </Button>
                <Button variant="outline" size="sm" className="w-full">
                  Add to Calendar
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </motion.div>
  );

  const renderCurrentScreen = () => {
    switch (currentScreen) {
      case 'home': return <Homepage />;
      case 'dashboard': return <Dashboard />;
      case 'planning': return <PlanningInterface />;
      case 'itinerary': return <ItineraryView />;
      case 'signin': return <SignInPage />;
      case 'signup': return <SignUpPage />;
      default: return <Homepage />;
    }
  };

  return (
    <AuthWrapper>
      <ConvexDebug />
      <div className="min-h-screen bg-white">
        <NavBar
          currentScreen={currentScreen}
          onNavigate={(screen) => {
            // Check if the screen requires authentication
            if ((screen === 'dashboard' || screen === 'guide') && !isSignedIn) {
              handleAuthenticatedAction(screen);
            } else {
              setCurrentScreen(screen);
            }
          }}
          rightContent={
            <>
              <SignedIn>
                <UserButton 
                  afterSignOutUrl="/"
                  appearance={{
                    elements: {
                      avatarBox: "w-10 h-10"
                    }
                  }}
                />
              </SignedIn>
              <SignedOut>
                <Button 
                  onClick={() => setCurrentScreen('signin')}
                  variant="ghost"
                  size="sm"
                >
                  Sign In
                </Button>
                <Button 
                  onClick={() => setCurrentScreen('signup')}
                  variant="primary"
                  size="sm"
                >
                  Sign Up
                </Button>
              </SignedOut>
            </>
          }
        />
        
        <AnimatePresence mode="wait">
          {renderCurrentScreen()}
        </AnimatePresence>
        
        {/* Toast notification */}
        {showToast && (
          <Toast
            message="Please sign in to access this feature"
            onClose={() => setShowToast(false)}
          />
        )}
      </div>
    </AuthWrapper>
  );
}

export default App;