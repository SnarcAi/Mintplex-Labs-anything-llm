/**
 * Recipe detail screen.
 */
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Image,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { api } from '../../services/api';
import { Recipe } from '../../types';

export default function RecipeDetailScreen({ route }: any) {
  const { recipeId } = route.params;
  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRecipe();
  }, []);

  const loadRecipe = async () => {
    try {
      const data = await api.getRecipe(recipeId);
      setRecipe(data);
    } catch (error) {
      console.error('Failed to load recipe:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLike = async () => {
    if (!recipe) return;

    try {
      if (recipe.is_liked) {
        await api.unlikeRecipe(recipeId);
        setRecipe({
          ...recipe,
          is_liked: false,
          like_count: recipe.like_count - 1,
        });
      } else {
        await api.likeRecipe(recipeId);
        setRecipe({
          ...recipe,
          is_liked: true,
          like_count: recipe.like_count + 1,
        });
      }
    } catch (error) {
      console.error('Failed to toggle like:', error);
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#ff6b35" />
      </View>
    );
  }

  if (!recipe) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.errorText}>Tarif bulunamadı</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Image source={{ uri: recipe.image_url }} style={styles.image} />

      <View style={styles.content}>
        <Text style={styles.title}>{recipe.title}</Text>

        <View style={styles.metaContainer}>
          <View style={styles.metaItem}>
            <Text style={styles.metaLabel}>Et Türü:</Text>
            <Text style={styles.metaValue}>{recipe.meat_type}</Text>
          </View>
          <View style={styles.metaItem}>
            <Text style={styles.metaLabel}>Zorluk:</Text>
            <Text style={styles.metaValue}>
              {recipe.difficulty === 1
                ? 'Kolay'
                : recipe.difficulty === 2
                ? 'Orta'
                : 'Zor'}
            </Text>
          </View>
        </View>

        <View style={styles.authorContainer}>
          <Image
            source={{
              uri: recipe.author.avatar_url || 'https://i.pravatar.cc/150',
            }}
            style={styles.authorAvatar}
          />
          <View>
            <Text style={styles.authorName}>{recipe.author.display_name}</Text>
            <Text style={styles.authorLevel}>{recipe.author.grill_level}</Text>
          </View>
        </View>

        <Text style={styles.description}>{recipe.description}</Text>

        <TouchableOpacity style={styles.likeButton} onPress={handleLike}>
          <Text style={styles.likeButtonText}>
            {recipe.is_liked ? '❤️' : '🤍'} {recipe.like_count} Beğeni
          </Text>
        </TouchableOpacity>
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
  errorText: {
    color: '#fff',
    fontSize: 16,
  },
  image: {
    width: '100%',
    height: 300,
  },
  content: {
    padding: 20,
  },
  title: {
    color: '#fff',
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 15,
  },
  metaContainer: {
    flexDirection: 'row',
    marginBottom: 20,
  },
  metaItem: {
    marginRight: 30,
  },
  metaLabel: {
    color: '#888',
    fontSize: 14,
  },
  metaValue: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  authorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
    paddingBottom: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#2a2a2a',
  },
  authorAvatar: {
    width: 50,
    height: 50,
    borderRadius: 25,
    marginRight: 15,
  },
  authorName: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  authorLevel: {
    color: '#ff6b35',
    fontSize: 14,
  },
  description: {
    color: '#ccc',
    fontSize: 16,
    lineHeight: 24,
    marginBottom: 30,
  },
  likeButton: {
    backgroundColor: '#ff6b35',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  likeButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});
