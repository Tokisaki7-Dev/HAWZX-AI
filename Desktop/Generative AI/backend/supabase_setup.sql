-- Tabela para armazenar gerações de imagens da IA
CREATE TABLE IF NOT EXISTS generations (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  prompt TEXT NOT NULL,
  image_base64 TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índice para buscar por data
CREATE INDEX idx_generations_created_at ON generations(created_at DESC);

-- Habilitar Row Level Security (RLS)
ALTER TABLE generations ENABLE ROW LEVEL SECURITY;

-- Política para permitir leitura pública
CREATE POLICY "Permitir leitura pública de gerações"
  ON generations
  FOR SELECT
  USING (true);

-- Política para permitir inserção autenticada (ou pública se quiser)
CREATE POLICY "Permitir inserção de gerações"
  ON generations
  FOR INSERT
  WITH CHECK (true);
