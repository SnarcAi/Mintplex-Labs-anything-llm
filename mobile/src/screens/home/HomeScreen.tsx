/**
 * Home screen - shows live rooms and latest recipes.
 */
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  Image,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { api } from '../../services/api';
import { LiveRoom, Recipe } from '../../types';
import { useAuth } from '../../utils/AuthContext';

export default function HomeScreen({ navigation }: any) {
  const { user, logout } = useAuth();
  const [liveRooms, setLiveRooms] = useState<LiveRoom[]>([]);
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [roomsData, recipesData] = await Promise.all([
        api.getLiveRooms(5),
        api.getRecipes('latest', 10),
      ]);
      setLiveRooms(roomsData);
      setRecipes(recipesData);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadData();
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#ff6b35" />
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>Merhaba, {user?.display_name}!</Text>
          <Text style={styles.level}>{user?.grill_level}</Text>
        </View>
        <TouchableOpacity onPress={() => navigation.navigate('Profile')}>
          <Image
            source={{ uri: user?.avatar_url || 'https://i.pravatar.cc/150' }}
            style={styles.avatar}
          />
        </TouchableOpacity>
      </View>

      {/* Live Rooms */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>🔴 Canlı Yayınlar</Text>
          <TouchableOpacity onPress={() => navigation.navigate('Live')}>
            <Text style={styles.seeAll}>Tümü</Text>
          </TouchableOpacity>
        </View>

        {liveRooms.length === 0 ? (
          <Text style={styles.emptyText}>Şu anda canlı yayın yok</Text>
        ) : (
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            {liveRooms.map((room) => (
              <TouchableOpacity
                key={room.id}
                style={styles.liveCard}
                onPress={() => navigation.navigate('Room', { roomId: room.id })}
              >
                <View style={styles.liveTag}>
                  <Text style={styles.liveTagText}>CANLI</Text>
                </View>
                <Text style={styles.liveTitle}>{room.title}</Text>
                <Text style={styles.liveHost}>{room.host.display_name}</Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        )}
      </View>

      {/* Latest Recipes */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>📖 Son Tarifler</Text>
          <TouchableOpacity onPress={() => navigation.navigate('Recipes')}>
            <Text style={styles.seeAll}>Tümü</Text>
          </TouchableOpacity>
        </View>

        {recipes.map((recipe) => (
          <TouchableOpacity
            key={recipe.id}
            style={styles.recipeCard}
            onPress={() =>
              navigation.navigate('RecipeDetail', { recipeId: recipe.id })
            }
          >
            <Image
              source={{ uri: recipe.image_url }}
              style={styles.recipeImage}
            />
            <View style={styles.recipeInfo}>
              <Text style={styles.recipeTitle}>{recipe.title}</Text>
              <Text style={styles.recipeAuthor}>
                {recipe.author.display_name}
              </Text>
              <Text style={styles.recipeLikes}>❤️ {recipe.like_count}</Text>
            </View>
          </TouchableOpacity>
        ))}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
  },
  loadingContainer: {
    flex: 1,
    backgroundColor: '#1a1a1a',
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
  },
  greeting: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  level: {
    fontSize: 14,
    color: '#ff6b35',
    marginTop: 4,
  },
  avatar: {
    width: 50,
    height: 50,
    borderRadius: 25,
  },
  section: {
    marginBottom: 30,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    marginBottom: 15,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
  },
  seeAll: {
    fontSize: 14,
    color: '#ff6b35',
  },
  emptyText: {
    color: '#666',
    textAlign: 'center',
    paddingVertical: 20,
  },
  liveCard: {
    width: 200,
    height: 120,
    backgroundColor: '#2a2a2a',
    borderRadius: 12,
    padding: 15,
    marginLeft: 20,
    justifyContent: 'space-between',
  },
  liveTag: {
    backgroundColor: '#ff0000',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
    alignSelf: 'flex-start',
  },
  liveTagText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  liveTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  liveHost: {
    color: '#888',
    fontSize: 14,
  },
  recipeCard: {
    flexDirection: 'row',
    backgroundColor: '#2a2a2a',
    borderRadius: 12,
    marginHorizontal: 20,
    marginBottom: 15,
    overflow: 'hidden',
  },
  recipeImage: {
    width: 100,
    height: 100,
  },
  recipeInfo: {
    flex: 1,
    padding: 15,
    justifyContent: 'space-between',
  },
  recipeTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  recipeAuthor: {
    color: '#888',
    fontSize: 14,
  },
  recipeLikes: {
    color: '#ff6b35',
    fontSize: 14,
  },
});
