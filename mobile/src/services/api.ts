/**
 * API client for MissYak Social backend.
 */
import axios, { AxiosInstance } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import {
  User,
  AuthResponse,
  LiveRoom,
  LiveRoomMessage,
  LiveRoomToken,
  Recipe,
  Product,
} from '../types';

// Change this to your backend URL
const API_BASE_URL = __DEV__
  ? 'http://localhost:8000/api/v1'
  : 'https://api.missyak.com/api/v1';

const TOKEN_KEY = '@missyak_token';

class ApiClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add token to requests
    this.client.interceptors.request.use(async (config) => {
      if (this.token) {
        config.headers.Authorization = `Bearer ${this.token}`;
      }
      return config;
    });

    // Load token on init
    this.loadToken();
  }

  private async loadToken() {
    try {
      const token = await AsyncStorage.getItem(TOKEN_KEY);
      if (token) {
        this.token = token;
      }
    } catch (error) {
      console.error('Failed to load token:', error);
    }
  }

  async setToken(token: string) {
    this.token = token;
    await AsyncStorage.setItem(TOKEN_KEY, token);
  }

  async clearToken() {
    this.token = null;
    await AsyncStorage.removeItem(TOKEN_KEY);
  }

  // Auth APIs
  async register(
    email: string,
    password: string,
    displayName: string,
    grillLevel: string = 'CAYLAK'
  ): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/auth/register', {
      email,
      password,
      display_name: displayName,
      grill_level: grillLevel,
    });
    await this.setToken(response.data.access_token);
    return response.data;
  }

  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/auth/login', {
      email,
      password,
    });
    await this.setToken(response.data.access_token);
    return response.data;
  }

  async getMe(): Promise<User> {
    const response = await this.client.get<User>('/auth/me');
    return response.data;
  }

  async logout() {
    await this.clearToken();
  }

  // User APIs
  async getUser(userId: string): Promise<User> {
    const response = await this.client.get<User>(`/users/${userId}`);
    return response.data;
  }

  async updateProfile(data: {
    display_name?: string;
    bio?: string;
    grill_level?: string;
    avatar_url?: string;
  }): Promise<User> {
    const response = await this.client.patch<User>('/users/me', data);
    return response.data;
  }

  // Live Room APIs
  async createRoom(title: string, description?: string): Promise<LiveRoom> {
    const response = await this.client.post<LiveRoom>('/rooms', {
      title,
      description,
    });
    return response.data;
  }

  async startRoom(roomId: string): Promise<LiveRoomToken> {
    const response = await this.client.post<LiveRoomToken>(
      `/rooms/${roomId}/start`
    );
    return response.data;
  }

  async joinRoom(roomId: string): Promise<LiveRoomToken> {
    const response = await this.client.post<LiveRoomToken>(
      `/rooms/${roomId}/join`
    );
    return response.data;
  }

  async endRoom(roomId: string): Promise<LiveRoom> {
    const response = await this.client.post<LiveRoom>(`/rooms/${roomId}/end`);
    return response.data;
  }

  async getLiveRooms(limit = 20, offset = 0): Promise<LiveRoom[]> {
    const response = await this.client.get<{ rooms: LiveRoom[]; total: number }>(
      '/rooms/live',
      { params: { limit, offset } }
    );
    return response.data.rooms;
  }

  async getRoom(roomId: string): Promise<LiveRoom> {
    const response = await this.client.get<LiveRoom>(`/rooms/${roomId}`);
    return response.data;
  }

  async getRoomMessages(
    roomId: string,
    limit = 50,
    offset = 0
  ): Promise<LiveRoomMessage[]> {
    const response = await this.client.get<LiveRoomMessage[]>(
      `/rooms/${roomId}/messages`,
      { params: { limit, offset } }
    );
    return response.data;
  }

  async sendRoomMessage(
    roomId: string,
    message: string
  ): Promise<LiveRoomMessage> {
    const response = await this.client.post<LiveRoomMessage>(
      `/rooms/${roomId}/messages`,
      { message_text: message }
    );
    return response.data;
  }

  // Recipe APIs
  async createRecipe(data: {
    title: string;
    description: string;
    image_url: string;
    meat_type: string;
    difficulty: number;
  }): Promise<Recipe> {
    const response = await this.client.post<Recipe>('/recipes', data);
    return response.data;
  }

  async getRecipes(
    sort: 'latest' | 'top' = 'latest',
    limit = 20,
    offset = 0
  ): Promise<Recipe[]> {
    const response = await this.client.get<{ recipes: Recipe[]; total: number }>(
      '/recipes',
      { params: { sort, limit, offset } }
    );
    return response.data.recipes;
  }

  async getRecipe(recipeId: string): Promise<Recipe> {
    const response = await this.client.get<Recipe>(`/recipes/${recipeId}`);
    return response.data;
  }

  async likeRecipe(recipeId: string): Promise<void> {
    await this.client.post(`/recipes/${recipeId}/like`);
  }

  async unlikeRecipe(recipeId: string): Promise<void> {
    await this.client.delete(`/recipes/${recipeId}/like`);
  }

  // Product APIs
  async getProducts(
    category?: string,
    limit = 20,
    offset = 0
  ): Promise<Product[]> {
    const response = await this.client.get<{ products: Product[]; total: number }>(
      '/shop/products',
      { params: { category, limit, offset } }
    );
    return response.data.products;
  }

  async getProduct(productId: string): Promise<Product> {
    const response = await this.client.get<Product>(
      `/shop/products/${productId}`
    );
    return response.data;
  }
}

export const api = new ApiClient();
