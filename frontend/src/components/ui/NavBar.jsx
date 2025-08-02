import { motion, AnimatePresence } from 'framer-motion';
import { Plane, Menu, X } from 'lucide-react';
import { useState } from 'react';
import { useUser } from '@clerk/clerk-react';
import { cn } from '../../utils/cn';

export function NavBar({ 
  currentScreen, 
  onNavigate, 
  leftContent, 
  rightContent,
  className 
}) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { isSignedIn } = useUser();

  // Define all navigation items with authentication requirements
  const allNavItems = [
    { id: 'home', label: 'Home', screen: 'home', public: true },
    { id: 'dashboard', label: 'My Trips', screen: 'dashboard', requiresAuth: true },
    { id: 'guide', label: 'Destinations', screen: 'guide', requiresAuth: true },
  ];

  // Filter navigation items based on authentication state
  const navItems = allNavItems.filter(item => 
    item.public || (item.requiresAuth && isSignedIn)
  );

  return (
    <>
      <motion.nav
        className={cn(
          "fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-lg border-b border-neutral-200",
          className
        )}
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <motion.div
              className="flex items-center space-x-2 cursor-pointer"
              onClick={() => onNavigate('home')}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              >
                <Plane className="h-8 w-8 text-primary-600" />
              </motion.div>
              <span className="text-xl font-bold gradient-text">TravelAI</span>
            </motion.div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-1">
              {navItems.map((item) => (
                <motion.button
                  key={item.id}
                  onClick={() => onNavigate(item.screen)}
                  className={cn(
                    "px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                    "relative overflow-hidden",
                    currentScreen === item.screen
                      ? "text-primary-600"
                      : "text-neutral-700 hover:text-primary-600"
                  )}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  {currentScreen === item.screen && (
                    <motion.div
                      className="absolute inset-0 bg-primary-50 rounded-lg -z-10"
                      layoutId="navbar-active"
                      transition={{ type: "spring", stiffness: 500, damping: 30 }}
                    />
                  )}
                  {item.label}
                </motion.button>
              ))}
            </div>

            {/* Right Content */}
            <div className="flex items-center space-x-4">
              {rightContent}
              
              {/* Mobile Menu Button */}
              <motion.button
                className="md:hidden p-2 rounded-lg hover:bg-neutral-100"
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {isMobileMenuOpen ? (
                  <X className="h-6 w-6 text-neutral-700" />
                ) : (
                  <Menu className="h-6 w-6 text-neutral-700" />
                )}
              </motion.button>
            </div>
          </div>
        </div>
      </motion.nav>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            className="fixed inset-0 z-40 md:hidden"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            {/* Backdrop */}
            <motion.div
              className="absolute inset-0 bg-black/50"
              onClick={() => setIsMobileMenuOpen(false)}
            />
            
            {/* Menu */}
            <motion.div
              className="absolute top-16 left-0 right-0 bg-white shadow-xl"
              initial={{ y: -20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: -20, opacity: 0 }}
              transition={{ type: "spring", stiffness: 300, damping: 30 }}
            >
              <div className="px-4 py-6 space-y-2">
                {navItems.map((item) => (
                  <motion.button
                    key={item.id}
                    onClick={() => {
                      onNavigate(item.screen);
                      setIsMobileMenuOpen(false);
                    }}
                    className={cn(
                      "w-full text-left px-4 py-3 rounded-lg text-base font-medium transition-all",
                      currentScreen === item.screen
                        ? "bg-primary-50 text-primary-600"
                        : "text-neutral-700 hover:bg-neutral-50"
                    )}
                    whileHover={{ x: 5 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    {item.label}
                  </motion.button>
                ))}
                
                <div className="pt-4 border-t border-neutral-200">
                  {leftContent}
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Spacer to prevent content from going under fixed navbar */}
      <div className="h-16" />
    </>
  );
}