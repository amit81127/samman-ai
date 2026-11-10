
export interface VocabItem {
  id: string;
  concept: string;
  label: string;
  category: string;
  icon: string;
  color: string;
}

export const CATEGORIES = [
  "Basic needs",
  "People",
  "Feelings",
  "Actions",
  "Health",
  "Everyday",
  "Food & Drinks",
  "Places",
  "Questions",
  "Time",
  "Social",
  "Education",
  "Safety",
  "Personal Care",
] as const;

export type VocabCategory = (typeof CATEGORIES)[number];

export const CATEGORY_COLORS: Record<VocabCategory, string> = {
  "Basic needs": "#EEF2FF",
  People: "#FDF2F8",
  Feelings: "#FEF3C7",
  Actions: "#EEF2FF",
  Health: "#FDE8E8",
  Everyday: "#E3F5F1",
  "Food & Drinks": "#FFF1E6",
  Places: "#E0F2FE",
  Questions: "#F3E8FF",
  Time: "#EDE9FE",
  Social: "#FCE7F3",
  Education: "#DBEAFE",
  Safety: "#FEE2E2",
  "Personal Care": "#CCFBF1",
};

export const DEFAULT_VOCAB: VocabItem[] = [
  // ==========================================
  // BASIC NEEDS
  // ==========================================
  { id: "i", concept: "I", label: "I", category: "Basic needs", icon: "👤", color: "#EEF2FF" },
  { id: "want", concept: "want", label: "Want", category: "Basic needs", icon: "✨", color: "#EEF2FF" },
  { id: "need", concept: "need", label: "Need", category: "Basic needs", icon: "⭐", color: "#EEF2FF" },
  { id: "water", concept: "water", label: "Water", category: "Basic needs", icon: "💧", color: "#E3F5F1" },
  { id: "food", concept: "food", label: "Food", category: "Basic needs", icon: "🍎", color: "#E3F5F1" },
  { id: "help", concept: "help", label: "Help", category: "Basic needs", icon: "🤝", color: "#FEF3C7" },
  { id: "rest", concept: "rest", label: "Rest", category: "Basic needs", icon: "😴", color: "#E3F5F1" },
  { id: "bathroom", concept: "bathroom", label: "Bathroom", category: "Basic needs", icon: "🚿", color: "#EEF2FF" },
  { id: "hungry", concept: "I am hungry", label: "Hungry", category: "Basic needs", icon: "🍽️", color: "#EEF2FF" },
  { id: "thirsty", concept: "I am thirsty", label: "Thirsty", category: "Basic needs", icon: "🥤", color: "#EEF2FF" },
  { id: "sleep", concept: "sleep", label: "Sleep", category: "Basic needs", icon: "🛏️", color: "#E3F5F1" },
  { id: "blanket", concept: "blanket", label: "Blanket", category: "Basic needs", icon: "🛌", color: "#E3F5F1" },
  { id: "pillow", concept: "pillow", label: "Pillow", category: "Basic needs", icon: "🧸", color: "#E3F5F1" },
  { id: "hot", concept: "I feel hot", label: "Hot", category: "Basic needs", icon: "🔥", color: "#FEF3C7" },
  { id: "cold", concept: "I feel cold", label: "Cold", category: "Basic needs", icon: "🥶", color: "#EEF2FF" },
  { id: "more_food", concept: "I want more food", label: "More Food", category: "Basic needs", icon: "🍛", color: "#E3F5F1" },
  { id: "finished", concept: "I am finished", label: "Finished", category: "Basic needs", icon: "✔️", color: "#E3F5F1" },
  { id: "alone", concept: "I want to be alone", label: "Alone", category: "Basic needs", icon: "🧍", color: "#EEF2FF" },
  { id: "comfortable", concept: "I want to be comfortable", label: "Comfort", category: "Basic needs", icon: "🛋️", color: "#E3F5F1" },

  // ==========================================
  // PEOPLE
  // ==========================================
  { id: "mom", concept: "mom", label: "Mom", category: "People", icon: "👩", color: "#FDF2F8" },
  { id: "dad", concept: "dad", label: "Dad", category: "People", icon: "👨", color: "#FDF2F8" },
  { id: "doctor", concept: "doctor", label: "Doctor", category: "People", icon: "👨‍⚕️", color: "#FDF2F8" },
  { id: "friend", concept: "friend", label: "Friend", category: "People", icon: "🧑", color: "#FDF2F8" },
  { id: "nurse", concept: "nurse", label: "Nurse", category: "People", icon: "👩‍⚕️", color: "#FDF2F8" },
  { id: "teacher", concept: "teacher", label: "Teacher", category: "People", icon: "👩‍🏫", color: "#FDF2F8" },
  { id: "brother", concept: "brother", label: "Brother", category: "People", icon: "👦", color: "#FDF2F8" },
  { id: "sister", concept: "sister", label: "Sister", category: "People", icon: "👧", color: "#FDF2F8" },
  { id: "grandma", concept: "grandmother", label: "Grandma", category: "People", icon: "👵", color: "#FDF2F8" },
  { id: "grandpa", concept: "grandfather", label: "Grandpa", category: "People", icon: "👴", color: "#FDF2F8" },
  { id: "baby", concept: "baby", label: "Baby", category: "People", icon: "👶", color: "#FDF2F8" },
  { id: "police", concept: "police officer", label: "Police", category: "People", icon: "👮", color: "#FDF2F8" },
  { id: "caregiver", concept: "caregiver", label: "Caregiver", category: "People", icon: "🤝", color: "#FDF2F8" },
  { id: "classmate", concept: "classmate", label: "Classmate", category: "People", icon: "🧑‍🎓", color: "#FDF2F8" },
  { id: "everyone", concept: "everyone", label: "Everyone", category: "People", icon: "👥", color: "#FDF2F8" },

  // ==========================================
  // FEELINGS
  // ==========================================
  { id: "happy", concept: "happy", label: "Happy", category: "Feelings", icon: "😊", color: "#FEF3C7" },
  { id: "sad", concept: "sad", label: "Sad", category: "Feelings", icon: "😢", color: "#FEF3C7" },
  { id: "pain", concept: "I feel pain", label: "Pain", category: "Feelings", icon: "😣", color: "#FEF3C7" },
  { id: "tired", concept: "tired", label: "Tired", category: "Feelings", icon: "😪", color: "#FEF3C7" },
  { id: "scared", concept: "scared", label: "Scared", category: "Feelings", icon: "😨", color: "#FEF3C7" },
  { id: "okay", concept: "okay", label: "Okay", category: "Feelings", icon: "👍", color: "#FEF3C7" },
  { id: "angry", concept: "angry", label: "Angry", category: "Feelings", icon: "😠", color: "#FEF3C7" },
  { id: "excited", concept: "excited", label: "Excited", category: "Feelings", icon: "🤩", color: "#FEF3C7" },
  { id: "worried", concept: "worried", label: "Worried", category: "Feelings", icon: "😟", color: "#FEF3C7" },
  { id: "confused", concept: "confused", label: "Confused", category: "Feelings", icon: "😕", color: "#FEF3C7" },
  { id: "bored", concept: "bored", label: "Bored", category: "Feelings", icon: "🥱", color: "#FEF3C7" },
  { id: "love", concept: "I love you", label: "Love", category: "Feelings", icon: "❤️", color: "#FDF2F8" },
  { id: "lonely", concept: "lonely", label: "Lonely", category: "Feelings", icon: "😔", color: "#FEF3C7" },
  { id: "surprised", concept: "surprised", label: "Surprised", category: "Feelings", icon: "😲", color: "#FEF3C7" },
  { id: "calm", concept: "calm", label: "Calm", category: "Feelings", icon: "😌", color: "#E3F5F1" },
  { id: "nervous", concept: "nervous", label: "Nervous", category: "Feelings", icon: "😬", color: "#FEF3C7" },
  { id: "proud", concept: "proud", label: "Proud", category: "Feelings", icon: "🥰", color: "#FEF3C7" },
  { id: "frustrated", concept: "frustrated", label: "Frustrated", category: "Feelings", icon: "😤", color: "#FEF3C7" },
  { id: "uncomfortable", concept: "uncomfortable", label: "Uncomfortable", category: "Feelings", icon: "😣", color: "#FEF3C7" },

  // ==========================================
  // ACTIONS
  // ==========================================
  { id: "go", concept: "go", label: "Go", category: "Actions", icon: "🚶", color: "#EEF2FF" },
  { id: "stop", concept: "stop", label: "Stop", category: "Actions", icon: "✋", color: "#EEF2FF" },
  { id: "yes", concept: "yes", label: "Yes", category: "Actions", icon: "✅", color: "#EEF2FF" },
  { id: "no", concept: "no", label: "No", category: "Actions", icon: "❌", color: "#EEF2FF" },
  { id: "more", concept: "more", label: "More", category: "Actions", icon: "➕", color: "#EEF2FF" },
  { id: "done", concept: "done", label: "Done", category: "Actions", icon: "✔️", color: "#EEF2FF" },
  { id: "come", concept: "come", label: "Come", category: "Actions", icon: "👋", color: "#EEF2FF" },
  { id: "wait", concept: "wait", label: "Wait", category: "Actions", icon: "⏳", color: "#EEF2FF" },
  { id: "open", concept: "open", label: "Open", category: "Actions", icon: "📂", color: "#EEF2FF" },
  { id: "close", concept: "close", label: "Close", category: "Actions", icon: "🚪", color: "#EEF2FF" },
  { id: "play", concept: "play", label: "Play", category: "Actions", icon: "🎮", color: "#EEF2FF" },
  { id: "read", concept: "read", label: "Read", category: "Actions", icon: "📖", color: "#EEF2FF" },
  { id: "write", concept: "write", label: "Write", category: "Actions", icon: "✍️", color: "#EEF2FF" },
  { id: "listen", concept: "listen", label: "Listen", category: "Actions", icon: "👂", color: "#EEF2FF" },
  { id: "look", concept: "look", label: "Look", category: "Actions", icon: "👀", color: "#EEF2FF" },
  { id: "give", concept: "give", label: "Give", category: "Actions", icon: "🎁", color: "#EEF2FF" },
  { id: "take", concept: "take", label: "Take", category: "Actions", icon: "🤲", color: "#EEF2FF" },
  { id: "again", concept: "again", label: "Again", category: "Actions", icon: "🔁", color: "#EEF2FF" },
  { id: "share", concept: "share", label: "Share", category: "Actions", icon: "🤝", color: "#EEF2FF" },
  { id: "choose", concept: "choose", label: "Choose", category: "Actions", icon: "☝️", color: "#EEF2FF" },
  { id: "walk", concept: "walk", label: "Walk", category: "Actions", icon: "🚶", color: "#EEF2FF" },
  { id: "run", concept: "run", label: "Run", category: "Actions", icon: "🏃", color: "#EEF2FF" },
  { id: "sit", concept: "sit", label: "Sit", category: "Actions", icon: "🪑", color: "#EEF2FF" },
  { id: "stand", concept: "stand", label: "Stand", category: "Actions", icon: "🧍", color: "#EEF2FF" },
  { id: "dance", concept: "dance", label: "Dance", category: "Actions", icon: "💃", color: "#EEF2FF" },

  // ==========================================
  // HEALTH
  // ==========================================
  { id: "medicine", concept: "medicine", label: "Medicine", category: "Health", icon: "💊", color: "#FDE8E8" },
  { id: "hurt", concept: "I am hurt", label: "Hurt", category: "Health", icon: "🩹", color: "#FDE8E8" },
  { id: "sick", concept: "I am sick", label: "Sick", category: "Health", icon: "🤒", color: "#FDE8E8" },
  { id: "better", concept: "I feel better", label: "Better", category: "Health", icon: "💚", color: "#FDE8E8" },
  { id: "headache", concept: "I have a headache", label: "Headache", category: "Health", icon: "🤕", color: "#FDE8E8" },
  { id: "stomachache", concept: "I have a stomachache", label: "Stomachache", category: "Health", icon: "🤢", color: "#FDE8E8" },
  { id: "fever", concept: "I have a fever", label: "Fever", category: "Health", icon: "🌡️", color: "#FDE8E8" },
  { id: "cough", concept: "I have a cough", label: "Cough", category: "Health", icon: "😷", color: "#FDE8E8" },
  { id: "dizzy", concept: "I feel dizzy", label: "Dizzy", category: "Health", icon: "😵", color: "#FDE8E8" },
  { id: "itchy", concept: "I feel itchy", label: "Itchy", category: "Health", icon: "🖐️", color: "#FDE8E8" },
  { id: "nausea", concept: "I feel nauseous", label: "Nauseous", category: "Health", icon: "🤢", color: "#FDE8E8" },
  { id: "breathing", concept: "I have difficulty breathing", label: "Breathing Problem", category: "Health", icon: "🫁", color: "#FDE8E8" },
  { id: "emergency", concept: "This is an emergency", label: "Emergency", category: "Health", icon: "🚨", color: "#FDE8E8" },
  { id: "hospital", concept: "hospital", label: "Hospital", category: "Health", icon: "🏥", color: "#FDE8E8" },
  { id: "ambulance", concept: "ambulance", label: "Ambulance", category: "Health", icon: "🚑", color: "#FDE8E8" },
  { id: "allergy", concept: "I have an allergy", label: "Allergy", category: "Health", icon: "🤧", color: "#FDE8E8" },

  // ==========================================
  // EVERYDAY
  // ==========================================
  { id: "home", concept: "home", label: "Home", category: "Everyday", icon: "🏠", color: "#E3F5F1" },
  { id: "outside", concept: "outside", label: "Outside", category: "Everyday", icon: "🌳", color: "#E3F5F1" },
  { id: "tv", concept: "TV", label: "TV", category: "Everyday", icon: "📺", color: "#E3F5F1" },
  { id: "music", concept: "music", label: "Music", category: "Everyday", icon: "🎵", color: "#E3F5F1" },
  { id: "phone", concept: "phone", label: "Phone", category: "Everyday", icon: "📱", color: "#E3F5F1" },
  { id: "car", concept: "car", label: "Car", category: "Everyday", icon: "🚗", color: "#E3F5F1" },
  { id: "bus", concept: "bus", label: "Bus", category: "Everyday", icon: "🚌", color: "#E3F5F1" },
  { id: "park", concept: "park", label: "Park", category: "Everyday", icon: "🏞️", color: "#E3F5F1" },
  { id: "computer", concept: "computer", label: "Computer", category: "Everyday", icon: "💻", color: "#E3F5F1" },
  { id: "game", concept: "game", label: "Game", category: "Everyday", icon: "🎲", color: "#E3F5F1" },
  { id: "rain", concept: "rain", label: "Rain", category: "Everyday", icon: "🌧️", color: "#E3F5F1" },
  { id: "sun", concept: "sun", label: "Sun", category: "Everyday", icon: "☀️", color: "#E3F5F1" },
  { id: "night", concept: "night", label: "Night", category: "Everyday", icon: "🌙", color: "#E3F5F1" },
  { id: "morning", concept: "morning", label: "Morning", category: "Everyday", icon: "🌅", color: "#E3F5F1" },
  { id: "birthday", concept: "birthday", label: "Birthday", category: "Everyday", icon: "🎂", color: "#E3F5F1" },
  { id: "festival", concept: "festival", label: "Festival", category: "Everyday", icon: "🎉", color: "#E3F5F1" },
  { id: "money", concept: "money", label: "Money", category: "Everyday", icon: "💰", color: "#E3F5F1" },

  // ==========================================
  // FOOD & DRINKS
  // ==========================================
  { id: "milk", concept: "milk", label: "Milk", category: "Food & Drinks", icon: "🥛", color: "#FFF1E6" },
  { id: "juice", concept: "juice", label: "Juice", category: "Food & Drinks", icon: "🧃", color: "#FFF1E6" },
  { id: "rice", concept: "rice", label: "Rice", category: "Food & Drinks", icon: "🍚", color: "#FFF1E6" },
  { id: "bread", concept: "bread", label: "Bread", category: "Food & Drinks", icon: "🍞", color: "#FFF1E6" },
  { id: "fruit", concept: "fruit", label: "Fruit", category: "Food & Drinks", icon: "🍉", color: "#FFF1E6" },
  { id: "banana", concept: "banana", label: "Banana", category: "Food & Drinks", icon: "🍌", color: "#FFF1E6" },
  { id: "apple", concept: "apple", label: "Apple", category: "Food & Drinks", icon: "🍎", color: "#FFF1E6" },
  { id: "egg", concept: "egg", label: "Egg", category: "Food & Drinks", icon: "🥚", color: "#FFF1E6" },
  { id: "vegetables", concept: "vegetables", label: "Vegetables", category: "Food & Drinks", icon: "🥕", color: "#FFF1E6" },
  { id: "icecream", concept: "ice cream", label: "Ice Cream", category: "Food & Drinks", icon: "🍦", color: "#FFF1E6" },
  { id: "tea", concept: "tea", label: "Tea", category: "Food & Drinks", icon: "🍵", color: "#FFF1E6" },
  { id: "coffee", concept: "coffee", label: "Coffee", category: "Food & Drinks", icon: "☕", color: "#FFF1E6" },
  { id: "biscuit", concept: "biscuit", label: "Biscuit", category: "Food & Drinks", icon: "🍪", color: "#FFF1E6" },

  // ==========================================
  // PLACES
  // ==========================================
  { id: "school", concept: "school", label: "School", category: "Places", icon: "🏫", color: "#E0F2FE" },
  { id: "classroom", concept: "classroom", label: "Classroom", category: "Places", icon: "📚", color: "#E0F2FE" },
  { id: "market", concept: "market", label: "Market", category: "Places", icon: "🛒", color: "#E0F2FE" },
  { id: "shop", concept: "shop", label: "Shop", category: "Places", icon: "🏪", color: "#E0F2FE" },
  { id: "garden", concept: "garden", label: "Garden", category: "Places", icon: "🌻", color: "#E0F2FE" },
  { id: "restaurant", concept: "restaurant", label: "Restaurant", category: "Places", icon: "🍽️", color: "#E0F2FE" },
  { id: "bedroom", concept: "bedroom", label: "Bedroom", category: "Places", icon: "🛏️", color: "#E0F2FE" },
  { id: "kitchen", concept: "kitchen", label: "Kitchen", category: "Places", icon: "🍳", color: "#E0F2FE" },
  { id: "playground", concept: "playground", label: "Playground", category: "Places", icon: "🛝", color: "#E0F2FE" },
  { id: "church", concept: "place of worship", label: "Place of Worship", category: "Places", icon: "🙏", color: "#E0F2FE" },

  // ==========================================
  // QUESTIONS
  // ==========================================
  { id: "what", concept: "what", label: "What?", category: "Questions", icon: "❓", color: "#F3E8FF" },
  { id: "where", concept: "where", label: "Where?", category: "Questions", icon: "📍", color: "#F3E8FF" },
  { id: "who", concept: "who", label: "Who?", category: "Questions", icon: "👤", color: "#F3E8FF" },
  { id: "when", concept: "when", label: "When?", category: "Questions", icon: "🕒", color: "#F3E8FF" },
  { id: "why", concept: "why", label: "Why?", category: "Questions", icon: "🤔", color: "#F3E8FF" },
  { id: "how", concept: "how", label: "How?", category: "Questions", icon: "💭", color: "#F3E8FF" },
  { id: "which", concept: "which", label: "Which?", category: "Questions", icon: "☝️", color: "#F3E8FF" },

  // ==========================================
  // TIME
  // ==========================================
  { id: "today", concept: "today", label: "Today", category: "Time", icon: "📅", color: "#EDE9FE" },
  { id: "tomorrow", concept: "tomorrow", label: "Tomorrow", category: "Time", icon: "🌅", color: "#EDE9FE" },
  { id: "yesterday", concept: "yesterday", label: "Yesterday", category: "Time", icon: "🗓️", color: "#EDE9FE" },
  { id: "now", concept: "now", label: "Now", category: "Time", icon: "⏰", color: "#EDE9FE" },
  { id: "later", concept: "later", label: "Later", category: "Time", icon: "⌛", color: "#EDE9FE" },
  { id: "soon", concept: "soon", label: "Soon", category: "Time", icon: "⏳", color: "#EDE9FE" },

  // ==========================================
  // SOCIAL
  // ==========================================
  { id: "hello", concept: "hello", label: "Hello", category: "Social", icon: "👋", color: "#FCE7F3" },
  { id: "goodbye", concept: "goodbye", label: "Goodbye", category: "Social", icon: "👋", color: "#FCE7F3" },
  { id: "please", concept: "please", label: "Please", category: "Social", icon: "🙏", color: "#FCE7F3" },
  { id: "thankyou", concept: "thank you", label: "Thank You", category: "Social", icon: "💖", color: "#FCE7F3" },
  { id: "sorry", concept: "sorry", label: "Sorry", category: "Social", icon: "🙏", color: "#FCE7F3" },
  { id: "welcome", concept: "you are welcome", label: "Welcome", category: "Social", icon: "😊", color: "#FCE7F3" },
  { id: "excuse", concept: "excuse me", label: "Excuse Me", category: "Social", icon: "🙋", color: "#FCE7F3" },
  { id: "goodmorning", concept: "good morning", label: "Good Morning", category: "Social", icon: "🌞", color: "#FCE7F3" },

  // ==========================================
  // EDUCATION
  // ==========================================
  { id: "learn", concept: "learn", label: "Learn", category: "Education", icon: "📚", color: "#DBEAFE" },
  { id: "homework", concept: "homework", label: "Homework", category: "Education", icon: "📝", color: "#DBEAFE" },
  { id: "exam", concept: "exam", label: "Exam", category: "Education", icon: "📋", color: "#DBEAFE" },
  { id: "pencil", concept: "pencil", label: "Pencil", category: "Education", icon: "✏️", color: "#DBEAFE" },
  { id: "draw", concept: "draw", label: "Draw", category: "Education", icon: "🎨", color: "#DBEAFE" },
  { id: "count", concept: "count", label: "Count", category: "Education", icon: "🔢", color: "#DBEAFE" },
  { id: "question", concept: "I have a question", label: "I Have a Question", category: "Education", icon: "🙋", color: "#DBEAFE" },
  { id: "understand", concept: "I understand", label: "Understand", category: "Education", icon: "💡", color: "#DBEAFE" },
  { id: "dont_understand", concept: "I do not understand", label: "Don't Understand", category: "Education", icon: "❔", color: "#DBEAFE" },

  // ==========================================
  // SAFETY
  // ==========================================
  { id: "danger", concept: "danger", label: "Danger", category: "Safety", icon: "⚠️", color: "#FEE2E2" },
  { id: "fire", concept: "fire", label: "Fire", category: "Safety", icon: "🔥", color: "#FEE2E2" },
  { id: "safe", concept: "I am safe", label: "Safe", category: "Safety", icon: "🛡️", color: "#FEE2E2" },
  { id: "call_help", concept: "please call for help", label: "Call for Help", category: "Safety", icon: "📞", color: "#FEE2E2" },
  { id: "lost", concept: "I am lost", label: "Lost", category: "Safety", icon: "🧭", color: "#FEE2E2" },
  { id: "dont_touch", concept: "do not touch me", label: "Don't Touch", category: "Safety", icon: "✋", color: "#FEE2E2" },
  { id: "stop_hurting", concept: "please stop hurting me", label: "Stop Hurting Me", category: "Safety", icon: "🛑", color: "#FEE2E2" },

  // ==========================================
  // PERSONAL CARE
  // ==========================================
  { id: "brush", concept: "brush my teeth", label: "Brush Teeth", category: "Personal Care", icon: "🪥", color: "#CCFBF1" },
  { id: "bath", concept: "take a bath", label: "Bath", category: "Personal Care", icon: "🛁", color: "#CCFBF1" },
  { id: "wash_hands", concept: "wash my hands", label: "Wash Hands", category: "Personal Care", icon: "🧼", color: "#CCFBF1" },
  { id: "comb", concept: "comb my hair", label: "Comb Hair", category: "Personal Care", icon: "💇", color: "#CCFBF1" },
  { id: "dress", concept: "get dressed", label: "Get Dressed", category: "Personal Care", icon: "👕", color: "#CCFBF1" },
  { id: "change_clothes", concept: "change my clothes", label: "Change Clothes", category: "Personal Care", icon: "👖", color: "#CCFBF1" },
];

// ==========================================
// UTILITY FUNCTIONS
// ==========================================

// Get vocabulary by category
export const getVocabByCategory = (
  category: string
): VocabItem[] => {
  return DEFAULT_VOCAB.filter(
    (item) => item.category === category
  );
};

// Search vocabulary
export const searchVocab = (
  query: string
): VocabItem[] => {
  const normalizedQuery = query.trim().toLowerCase();

  if (!normalizedQuery) return DEFAULT_VOCAB;

  return DEFAULT_VOCAB.filter((item) =>
    [
      item.id,
      item.label,
      item.concept,
      item.category,
    ].some((value) =>
      value.toLowerCase().includes(normalizedQuery)
    )
  );
};

// Validate unique IDs
export const validateVocabulary = (): boolean => {
  const ids = DEFAULT_VOCAB.map((item) => item.id);

  return new Set(ids).size === ids.length;
};

// Get category counts
export const getCategoryCounts = (): Record<string, number> => {
  return Object.fromEntries(
    CATEGORIES.map((category) => [
      category,
      getVocabByCategory(category).length,
    ])
  );
};
