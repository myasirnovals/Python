import math

def softmax(values):
    m=max(values)
    exps=[math.exp(v-m) for v in values]
    total=sum(exps)
    return [v/total for v in exps]

def dot(a,b):
    return sum(x*y for x,y in zip(a,b))

def attention_row(query,keys,values,mask=None):
    dk=len(query)
    scores=[dot(query,key)/math.sqrt(dk) for key in keys]
    if mask is not None:
        scores=[s if allowed else float("-inf") for s,allowed in zip(scores,mask)]
    weights=softmax(scores)
    output=[sum(weights[j]*values[j][d] for j in range(len(values)))
            for d in range(len(values[0]))]
    return scores,weights,output

def main():
    print("="*60+"\nDEMO TOKENISASI SEDERHANA DAN EMBEDDING\n"+"="*60)
    sentence="saya suka kopi"
    tokens=sentence.split()
    embeddings={"saya":[0.10,0.20],"suka":[0.30,0.40],"kopi":[0.50,0.60]}
    print("Kalimat:",sentence,"\nToken:",tokens)
    for t in tokens: print(f"{t:>6} -> {embeddings[t]}")
    print("\nCatatan: split() adalah tokenisasi sederhana, bukan BPE.")
    print("Vektor embedding di atas hanya angka ilustratif, bukan hasil training.")

    names=["saya","suka","kopi"]
    Q=[[1,0],[1,1],[2,1]]
    K=[[1,1],[0,1],[1,2]]
    V=[[0,1],[1,0],[1,1]]
    print("\n"+"="*60+"\nDEMO SCALED DOT-PRODUCT ATTENTION\n"+"="*60)
    print("Q =",Q,"\nK =",K,"\nV =",V)
    scores,weights,out=attention_row(Q[2],K,V)
    print("Query: kopi")
    print("Skor:",[round(x,4) for x in scores])
    print("Bobot softmax:",[round(x,4) for x in weights])
    print("Output:",[round(x,4) for x in out])
    print("Output contoh mendekati [0.69, 0.93].")

    print("\n"+"="*60+"\nDEMO CAUSAL MASK\n"+"="*60)
    scores,weights,out=attention_row(Q[1],K,V,mask=[True,True,False])
    print("Query: suka; hanya boleh melihat saya dan suka.")
    print("Skor setelah mask:",["-inf" if x==float("-inf") else round(x,4) for x in scores])
    print("Bobot setelah mask:",[round(x,4) for x in weights])
    print("Bobot token masa depan 'kopi' menjadi 0.")

if __name__=="__main__": main()
