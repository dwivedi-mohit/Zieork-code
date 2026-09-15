def partition_palindromes(s: str) -> list[list[str]]:
    res = []
    def is_palindrome(sub):
        return sub == sub[::-1]
    def backtrack(start, path):
        if start == len(s):
            res.append(list(path))
            return
        for end in range(start + 1, len(s) + 1):
            sub = s[start:end]
            if is_palindrome(sub):
                path.append(sub)
                backtrack(end, path)
                path.pop()
    backtrack(0, [])
    return res
