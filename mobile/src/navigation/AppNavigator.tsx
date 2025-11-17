/**
 * Main app navigation.
 */
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { useAuth } from '../utils/AuthContext';

// Auth Screens
import LoginScreen from '../screens/auth/LoginScreen';
import RegisterScreen from '../screens/auth/RegisterScreen';

// Main Tab Screens
import HomeScreen from '../screens/home/HomeScreen';
import LiveScreen from '../screens/live/LiveScreen';
import RecipesScreen from '../screens/recipes/RecipesScreen';
import ShopScreen from '../screens/shop/ShopScreen';

// Other Screens
import RoomScreen from '../screens/live/RoomScreen';
import CreateRoomScreen from '../screens/live/CreateRoomScreen';
import CreateRecipeScreen from '../screens/recipes/CreateRecipeScreen';
import RecipeDetailScreen from '../screens/recipes/RecipeDetailScreen';
import ProductDetailScreen from '../screens/shop/ProductDetailScreen';
import ProfileScreen from '../screens/profile/ProfileScreen';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={{
        tabBarStyle: { backgroundColor: '#1a1a1a' },
        tabBarActiveTintColor: '#ff6b35',
        tabBarInactiveTintColor: '#888',
        headerStyle: { backgroundColor: '#1a1a1a' },
        headerTintColor: '#fff',
      }}
    >
      <Tab.Screen
        name="Home"
        component={HomeScreen}
        options={{ title: 'Ana Sayfa' }}
      />
      <Tab.Screen
        name="Live"
        component={LiveScreen}
        options={{ title: 'Canlı Yayınlar' }}
      />
      <Tab.Screen
        name="Recipes"
        component={RecipesScreen}
        options={{ title: 'Tarifler' }}
      />
      <Tab.Screen
        name="Shop"
        component={ShopScreen}
        options={{ title: 'Mağaza' }}
      />
    </Tab.Navigator>
  );
}

export default function AppNavigator() {
  const { user, loading } = useAuth();

  if (loading) {
    return null; // Or a loading screen
  }

  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerStyle: { backgroundColor: '#1a1a1a' },
          headerTintColor: '#fff',
        }}
      >
        {!user ? (
          // Auth Stack
          <>
            <Stack.Screen
              name="Login"
              component={LoginScreen}
              options={{ headerShown: false }}
            />
            <Stack.Screen
              name="Register"
              component={RegisterScreen}
              options={{ title: 'Kayıt Ol' }}
            />
          </>
        ) : (
          // Main App Stack
          <>
            <Stack.Screen
              name="MainTabs"
              component={MainTabs}
              options={{ headerShown: false }}
            />
            <Stack.Screen
              name="Room"
              component={RoomScreen}
              options={{ title: 'Canlı Yayın' }}
            />
            <Stack.Screen
              name="CreateRoom"
              component={CreateRoomScreen}
              options={{ title: 'Yayın Oluştur' }}
            />
            <Stack.Screen
              name="CreateRecipe"
              component={CreateRecipeScreen}
              options={{ title: 'Tarif Ekle' }}
            />
            <Stack.Screen
              name="RecipeDetail"
              component={RecipeDetailScreen}
              options={{ title: 'Tarif Detayı' }}
            />
            <Stack.Screen
              name="ProductDetail"
              component={ProductDetailScreen}
              options={{ title: 'Ürün Detayı' }}
            />
            <Stack.Screen
              name="Profile"
              component={ProfileScreen}
              options={{ title: 'Profil' }}
            />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
