def calc_classical_security(n, h, k, t):
    def success_probability(q):
        prf_term = 10 * (q + 1) ** 2 / 2**(8 * n)
        itsr_term = 2 * (q + 1) * sum(
            (1 - (1 - 1 / t)**gamma)**k
            * binomial(q, gamma)
            * (1 - 1 / 2**h)**(q - gamma)
            * (1 / 2**h)**gamma
            for gamma in range(1, h+1)
        )
        return prf_term + itsr_term
    q = 1
    while success_probability(q) < 1:
        q *= 2
    return log(q, 2)


n=16
h=63
k=14
t=128
print (calc_classical_security(n, h, k, t))