def save_embeddings(savepath, data):
    with open(savepath, "w") as f:
        if isinstance(data, list):
            for image, embedding in data:
                f.write(image)
                f.write(",")
                for emb in embedding:
                    f.write(str(emb))
                    f.write(",")
                f.write("\n")
        else:
            f.write(data[0])
            f.write(",")
            for emb in data[1]:
                f.write(str(emb))
                f.write(",")
            f.write("\n")


def load_embeddings(embeddings_path):
    embeddings = []
    with open(embeddings_path, mode="r") as f:
        for row in f.readlines():
            separated = row.strip().split(",")[:-1]
            image_path = separated[0]
            embedding = separated[1:]
            embeddings.append((image_path, embedding))
    return embeddings


# Example usage
if __name__ == "__main__":
    mocknimi = "images/image0.png"
    mockemb = [1, 2, 3, 4, 2, 1, 2, 3]
    save_embeddings("temp/embeddings.csv", (mocknimi, mockemb))

    paar1 = ("images/image0.png", [1, 2, 3, 4, 2, 1, 2, 3])
    paar2 = ("images/image1.png", [1, 0, 0, 0, 0, 0, 0, 0])
    save_embeddings("temp/embeddings2.csv", [paar1, paar2])

    print("esimene")
    print(load_embeddings("temp/embeddings.csv"))

    print("teine")
    print(load_embeddings("temp/embeddings2.csv"))
