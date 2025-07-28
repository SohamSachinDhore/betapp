-- Add commission_type field to customers table

-- Add the column if it doesn't exist
ALTER TABLE customers ADD COLUMN commission_type TEXT DEFAULT 'commission' CHECK (commission_type IN ('commission', 'non_commission'));

-- Update existing customers to have 'commission' as default
UPDATE customers SET commission_type = 'commission' WHERE commission_type IS NULL;