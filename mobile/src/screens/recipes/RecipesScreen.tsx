/**
 * Recipes feed screen.
 */
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  TouchableOpacity,
  Image,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { api } from '../../services/api';
import { Recipe } from '../../types';

export default function RecipesScreen({ navigation }: any) {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [sort, setSort] = useState<'latest' | 'top'>('latest');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadRecipes();
  }, [sort]);

  const loadRecipes = async () => {
    try {
      const data = await api.getRecipes(sort);
      setRecipes(data);
    } catch (error) {
      console.error('Failed to load recipes:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadRecipes();
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#ff6b35" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={recipes}
        keyExtractor={(item) => item.id}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListHeaderComponent={
          <View style={styles.header}>
            <View style={styles.sortButtons}>
              <TouchableOpacity
                style={[styles.sortButton, sort === 'latest' && styles.sortButtonActive]}
                onPress={() => setSort('latest')}
              >
                <Text
                  style={[
                    styles.sortButtonText,
                    sort === 'latest' && styles.sortButtonTextActive,
                  ]}
                >
                  Son Eklenenler
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.sortButton, sort === 'top' && styles.sortButtonActive]}
                onPress={() => setSort('top')}
              >
                <Text
                  style={[
                    styles.sortButtonText,
                    sort === 'top' && styles.sortButtonTextActive,
                  ]}
                >
                  En Popüler
                </Text>
              </TouchableOpacity>
            </View>
            <TouchableOpacity
              style={styles.createButton}
              onPress={() => navigation.navigate('CreateRecipe')}
            >
              <Text style={styles.createButtonText}>+ Tarif Ekle</Text>
            </TouchableOpacity>
          </View>
        }
        renderItem={({ item }) => (
          <TouchableOpacity
            style={styles.recipeCard}
            onPress={() =>
              navigation.navigate('RecipeDetail', { recipeId: item.id })
            }
          >
            <Image source={{ uri: item.image_url }} style={styles.recipeImage} />
            <View style={styles.recipeInfo}>
              <Text style={styles.recipeTitle}>{item.title}</Text>
              <Text style={styles.recipeDescription} numberOfLines={2}>
                {item.description}
              </Text>
              <View style={styles.recipeFooter}>
                <Text style={styles.recipeAuthor}>
                  {item.author.display_name}
                </Text>
                <Text style={styles.recipeLikes}>❤️ {item.like_count}</Text>
              </View>
            </View>
          </TouchableOpacity>
        )}
      />
    </View>
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
    padding: 20,
  },
  sortButtons: {
    flexDirection: 'row',
    marginBottom: 15,
  },
  sortButton: {
    flex: 1,
    backgroundColor: '#2a2a2a',
    padding: 12,
    borderRadius: 8,
    marginHorizontal: 5,
    alignItems: 'center',
  },
  sortButtonActive: {
    backgroundColor: '#ff6b35',
  },
  sortButtonText: {
    color: '#888',
    fontWeight: 'bold',
  },
  sortButtonTextActive: {
    color: '#fff',
  },
  createButton: {
    backgroundColor: '#ff6b35',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  createButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  recipeCard: {
    backgroundColor: '#2a2a2a',
    margin: 15,
    marginTop: 0,
    borderRadius: 12,
    overflow: 'hidden',
  },
  recipeImage: {
    width: '100%',
    height: 200,
  },
  recipeInfo: {
    padding: 15,
  },
  recipeTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  recipeDescription: {
    color: '#aaa',
    fontSize: 14,
    marginBottom: 12,
  },
  recipeFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
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
