import Data.Char
import Data.List

data Token = LiteralToken String
           | KeywordToken String
           deriving (Show, Eq)

data Node = EqualNode
          | OnNode
          | OffNode
          | NumberNode Integer
           deriving (Show, Eq)

tokenize [] = []
tokenize s@(h:t)
  | not $ null literal               = LiteralToken literal : tokenize rest
  | isPrefixOf "off" (map toLower s) = KeywordToken "off"   : tokenize (drop 3 s)
  | isPrefixOf "on"  (map toLower s) = KeywordToken "on"    : tokenize (drop 2 s)
  | h == '='                         = KeywordToken "="     : tokenize t
  | otherwise          = tokenize t
  where (literal, rest) = span isDigit s

buildAST = map convertToken where
  convertToken (KeywordToken "=")   = EqualNode
  convertToken (KeywordToken "on")  = OnNode
  convertToken (KeywordToken "off") = OffNode
  convertToken (LiteralToken n)     = NumberNode (read n)

interpret :: [Node] -> [Integer]
interpret = (\(_, _, l) -> l) . foldl step (True, 0, []) where
  step (_, acc, l)      OnNode        = (True, acc, l)
  step (_, acc, l)      OffNode       = (False, acc, l)
  step (onoff, acc, l)  EqualNode     = (onoff, acc, acc:l)
  step (onoff, acc, l) (NumberNode n)
    | onoff     = (onoff, acc + n, l)
    | otherwise = (onoff, acc, l)

main = getContents >>= sequence . map (putStrLn . show) . interpret . buildAST . tokenize
