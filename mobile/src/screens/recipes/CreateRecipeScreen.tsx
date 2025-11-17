/**
 * Create recipe screen.
 * Note: Image upload functionality requires additional setup with expo-image-picker and backend upload endpoint.
 */
import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  ScrollView,
} from 'react-native';
import { api } from '../../services/api';
import { MeatType } from '../../types';

export default function CreateRecipeScreen({ navigation }: any) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [meatType, setMeatType] = useState<MeatType>(MeatType.KOFTE);
  const [difficulty, setDifficulty] = useState(1);
  const [imageUrl, setImageUrl] = useState('');
  const [loading, setLoading] = useState(false);

  const handleCreate = async () => {
    if (!title.trim() || !description.trim()) {
      Alert.alert('Hata', 'Lütfen tüm alanları doldurun');
      return;
    }

    setLoading(true);
    try {
      // For V1, use a placeholder image if not provided
      const finalImageUrl = imageUrl || 'https://placehold.co/600x400/2a2a2a/ffffff?text=Recipe';

      await api.createRecipe({
        title,
        description,
        image_url: finalImageUrl,
        meat_type: meatType,
        difficulty,
      });

      Alert.alert('Başarılı', 'Tarif eklendi!', [
        { text: 'Tamam', onPress: () => navigation.goBack() },
      ]);
    } catch (error: any) {
      Alert.alert('Hata', 'Tarif eklenemedi');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.label}>Tarif Başlığı *</Text>
      <TextInput
        style={styles.input}
        placeholder="Örn: Çökertme Kebap"
        placeholderTextColor="#666"
        value={title}
        onChangeText={setTitle}
      />

      <Text style={styles.label}>Açıklama *</Text>
      <TextInput
        style={[styles.input, styles.textArea]}
        placeholder="Tarifinizi detaylı anlatın..."
        placeholderTextColor="#666"
        value={description}
        onChangeText={setDescription}
        multiline
        numberOfLines={6}
      />

      <Text style={styles.label}>Et Türü</Text>
      <View style={styles.meatTypeContainer}>
        {Object.values(MeatType).map((type) => (
          <TouchableOpacity
            key={type}
            style={[
              styles.meatTypeButton,
              meatType === type && styles.meatTypeButtonActive,
            ]}
            onPress={() => setMeatType(type)}
          >
            <Text
              style={[
                styles.meatTypeText,
                meatType === type && styles.meatTypeTextActive,
              ]}
            >
              {type}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <Text style={styles.label}>Zorluk Seviyesi</Text>
      <View style={styles.difficultyContainer}>
        {[1, 2, 3].map((level) => (
          <TouchableOpacity
            key={level}
            style={[
              styles.difficultyButton,
              difficulty === level && styles.difficultyButtonActive,
            ]}
            onPress={() => setDifficulty(level)}
          >
            <Text
              style={[
                styles.difficultyText,
                difficulty === level && styles.difficultyTextActive,
              ]}
            >
              {level === 1 ? 'Kolay' : level === 2 ? 'Orta' : 'Zor'}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <Text style={styles.label}>Fotoğraf URL (opsiyonel)</Text>
      <TextInput
        style={styles.input}
        placeholder="https://..."
        placeholderTextColor="#666"
        value={imageUrl}
        onChangeText={setImageUrl}
        autoCapitalize="none"
      />

      <TouchableOpacity
        style={styles.button}
        onPress={handleCreate}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.buttonText}>Tarifi Paylaş</Text>
        )}
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
    padding: 20,
  },
  label: {
    color: '#fff',
    fontSize: 16,
    marginBottom: 8,
    marginTop: 15,
  },
  input: {
    backgroundColor: '#2a2a2a',
    color: '#fff',
    borderRadius: 8,
    padding: 15,
    fontSize: 16,
  },
  textArea: {
    height: 120,
    textAlignVertical: 'top',
  },
  meatTypeContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 10,
  },
  meatTypeButton: {
    backgroundColor: '#2a2a2a',
    padding: 10,
    borderRadius: 8,
    marginRight: 10,
    marginBottom: 10,
  },
  meatTypeButtonActive: {
    backgroundColor: '#ff6b35',
  },
  meatTypeText: {
    color: '#888',
    fontSize: 14,
  },
  meatTypeTextActive: {
    color: '#fff',
  },
  difficultyContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  difficultyButton: {
    flex: 1,
    backgroundColor: '#2a2a2a',
    padding: 12,
    borderRadius: 8,
    marginHorizontal: 5,
    alignItems: 'center',
  },
  difficultyButtonActive: {
    backgroundColor: '#ff6b35',
  },
  difficultyText: {
    color: '#888',
    fontSize: 14,
    fontWeight: 'bold',
  },
  difficultyTextActive: {
    color: '#fff',
  },
  button: {
    backgroundColor: '#ff6b35',
    borderRadius: 8,
    padding: 15,
    alignItems: 'center',
    marginTop: 30,
    marginBottom: 40,
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});
