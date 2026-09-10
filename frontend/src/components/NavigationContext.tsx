"use client";

import React, { createContext, useContext, useState } from "react";

interface NavContextType {
  isDrawerOpen: boolean;
  openDrawer: () => void;
  closeDrawer: () => void;
  toggleDrawer: () => void;
}

const NavigationContext = createContext<NavContextType>({
  isDrawerOpen: false,
  openDrawer: () => {},
  closeDrawer: () => {},
  toggleDrawer: () => {},
});

export const useNavigation = () => useContext(NavigationContext);

export const NavigationProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  return (
    <NavigationContext.Provider
      value={{
        isDrawerOpen,
        openDrawer: () => setIsDrawerOpen(true),
        closeDrawer: () => setIsDrawerOpen(false),
        toggleDrawer: () => setIsDrawerOpen((prev) => !prev),
      }}
    >
      {children}
    </NavigationContext.Provider>
  );
};
