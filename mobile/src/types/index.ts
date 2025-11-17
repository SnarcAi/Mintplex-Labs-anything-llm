/**
 * TypeScript types for MissYak Social app.
 */

export enum GrillLevel {
  CAYLAK = "CAYLAK",
  AMATOR = "AMATOR",
  USTA = "USTA",
}

export enum MeatType {
  KOFTE = "KOFTE",
  BONFILE = "BONFILE",
  BALIK = "BALIK",
  TAVUK = "TAVUK",
  OTHER = "OTHER",
}

export enum ProductCategory {
  GRILL = "GRILL",
  FUEL = "FUEL",
  ACCESSORY = "ACCESSORY",
  BUNDLE = "BUNDLE",
}

export enum RoomStatus {
  CREATED = "CREATED",
  LIVE = "LIVE",
  ENDED = "ENDED",
}

export interface User {
  id: string;
  email: string;
  display_name: string;
  avatar_url?: string;
  bio?: string;
  grill_level: GrillLevel;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface LiveRoom {
  id: string;
  host_user_id: string;
  host: User;
  title: string;
  description?: string;
  status: RoomStatus;
  provider_room_id?: string;
  created_at: string;
  started_at?: string;
  ended_at?: string;
  viewer_count?: number;
}

export interface LiveRoomMessage {
  id: string;
  room_id: string;
  user_id: string;
  user: User;
  message_text: string;
  created_at: string;
}

export interface LiveRoomToken {
  token: string;
  room_name: string;
  ws_url: string;
}

export interface Recipe {
  id: string;
  author_user_id: string;
  author: User;
  title: string;
  description: string;
  image_url: string;
  meat_type: MeatType;
  difficulty: number;
  like_count: number;
  created_at: string;
  is_liked: boolean;
}

export interface Product {
  id: string;
  name: string;
  description: string;
  image_url: string;
  price: string;
  currency: string;
  category: ProductCategory;
  external_url: string;
  is_active: boolean;
  created_at: string;
}
