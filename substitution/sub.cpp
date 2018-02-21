#include <fstream>
#include <iostream>
#include <string>
#include <vector>
#include <sstream>
#include <cmath>
#include <ctime>
#include <cstdlib>
using namespace std;


/*
    very slow currently!
    speed it up by dividing up wordlist by length,
    and only checking neighbors from the right length list.
*/
struct Node {
    string word;
    int distance;
    Node * previous;
};


vector<string> readWords(string file){
    ifstream in(file);
    vector<string> words;
    string line;
    while (getline(in, line)){
        if (line.length() > 1){
            words.push_back(line);
        }
    }
    in.close();
    return words;
}

bool verifyWord(string word, vector<string> wordlist){
    bool result = false;
    for (int x = 0; x < wordlist.size(); x++){
        if (wordlist[x] == word){
            return true;
        }
    }
    return result;
}

vector<string> removeDuplicates(vector<string> list){
    vector<string> result;
    for (int x = 0; x < list.size(); x++){
        bool found = false;
        for (int y = 0; y < result.size(); y++){
            if (list[x] == result[y]){
                found = true;
            }
        }
        if (!found){
            result.push_back(list[x]);
        }
    }
    return result;
}

vector<string> replacements (string word){
    vector<string> result;
    for (int x = 0; x < word.length(); x++){
        for (int y = 0; y < 26; y++){
            string temp = "";
            for (int z = 0; z < word.length(); z++){
                if (x == z){
                    temp += 'a' + y;
                } else {
                    temp += word[z];
                }
            }
            if (temp != word){
                result.push_back(temp);
            }
        }
    }
    result = removeDuplicates(result);
    return result;
}

vector<string> subtractions (string word){
    vector<string> result;
    for (int x = 0; x < word.length(); x++){
        string temp = "";
        for (int y = 0; y < word.length(); y++){
            if (x != y){
                temp += word[y];
            }
        }
        if (temp != word){
            result.push_back(temp);
        }
    }
    result = removeDuplicates(result);
    return result;
}

vector<string> additions (string word){
    vector<string> result;
    for (int x = 0; x < word.length(); x++){
        for (int y = 0; y < 26; y++){
            string temp = "";
            for (int z = 0; z < word.length(); z++){
                if (x == z){
                    temp += 'a' + y;
                }
                temp += word[z];
            }
            if (temp != word){
                result.push_back(temp);
            }
        }
    }
    for (int x = 0; x < 26; x++){
        string temp = word;
        temp += 'a' + x;
        if (temp != word){
            result.push_back(temp);
        }
    }
    result = removeDuplicates(result);
    return result;
}

string longestString(vector<string> words){
    string longest = "";
    for (int x = 0; x < words.size(); x++){
        if (words[x].length() > longest.length()){
            longest = words[x];
        }
    }
    return longest;
}

// not optimized, shouldn't badly impact performance
vector<vector<string> > wordsByLength(vector<string> words){
    vector<vector<string> > wordsByLength;
    for (int x = 1; x <= longestString(words).length(); x++){
        vector<string> thisLength;
        for (int y = 0; y < words.size(); y++){
            if (words[y].length() == x){
                thisLength.push_back(words[y]);
            }
        }
        wordsByLength.push_back(thisLength);
    }
    return wordsByLength;
}

vector<string> findNeighbors(string word, vector<vector<string> > wordlist){
    vector<string> result;
    vector<string> add = additions(word);
    vector<string> rep = replacements(word);
    vector<string> sub = subtractions(word);
    // check sub matches
    for (int x = 0; x < wordlist[word.length() - 2].size(); x++){
        for (int y = 0; y < sub.size(); y++){
            if (wordlist[word.length() - 2][x] == sub[y]){
                result.push_back(sub[y]);
            }
        }
    }
    // check rep matches
    for (int x = 0; x < wordlist[word.length() - 1].size(); x++){
        for (int y = 0; y < rep.size(); y++){
            if (wordlist[word.length() - 1][x] == rep[y]){
                result.push_back(rep[y]);
            }
        }
    }
    // check add matches
    for (int x = 0; x < wordlist[word.length()].size(); x++){
        for (int y = 0; y < add.size(); y++){
            if (wordlist[word.length()][x] == add[y]){
                result.push_back(add[y]);
            }
        }
    }
    
    return result;
}

void outputVector(vector<string> v){
    for (int x = 0; x < v.size(); x++){
        cout << v[x] << '\n';
    }
}

// to optimize: add a case to jump ship if our target word is in visited.
bool finished(vector<Node*> unvisited, vector<Node*> visited, string target){
    // If we've visited every node
    if (unvisited.size() == 0){
        cout << "None left to visit.\n";
        return true;
    }
    
    // If we can't reach any more nodes
    bool anyLeft = false;
    for (int x = 0; x < unvisited.size(); x++){
        if (unvisited[x]->distance != -1){
            anyLeft = true;
        }
    }
    if (!anyLeft){
        cout << "Only ones left are unreachable.\n";
        return true;
    }

    for (int x = 0; x < visited.size(); x++){
        if (visited[x]->word == target){
            cout << "Target reached!\n";
            return true;
        }
    }

    // Otherwise there's more to do
    return false;
}

void Dijkstra(string start, string finish, vector<vector<string> > words, int totalSize){
    Node * startNode = new Node();
    startNode->distance = 0;
    startNode->word = start;
    startNode->previous = 0;

    vector<Node*> unvisited;
    vector<Node*> visited;
    unvisited.push_back(startNode);
    int index = 0;

    while (!finished(unvisited, visited, finish)){
        //cout << unvisited[index]->word << '\n';
        vector<string> neighbors = findNeighbors(unvisited[index]->word, words);
        for (int x = 0; x < neighbors.size(); x++){
            Node * n = 0;
            for (int y = 0; y < unvisited.size(); y++){
                if (unvisited[y]->word == neighbors[x]){
                    n = unvisited[y];
                }
            }
            if (n == 0){
                Node * temp = new Node();
                temp->distance = unvisited[index]->distance + 1;
                temp->word = neighbors[x];
                temp->previous = unvisited[index];
                unvisited.push_back(temp);
            } else {
                if (n->distance == -1 || n->distance > unvisited[index]->distance + 1){
                    n->distance = unvisited[index]->distance + 1;
                    n->previous = unvisited[index];
                }
            }
        }
        // move our current node to visited
        visited.push_back(unvisited[index]);
        unvisited.erase(unvisited.begin() + index);
        // Output our progress
        if (visited.size() % 100 == 0){
            cout << "Amount visited: " << visited.size() << " out of " << totalSize << '\n';
        }
        // choose new current
        int minimum = -1;
        for (int x = 0; x < unvisited.size(); x++){
            if (unvisited[x]->distance != -1 && unvisited[x]->distance < minimum){
                minimum = unvisited[x]->distance;
                index = x;
            }
        }
    }

    for (int x = 0; x < visited.size(); x++){
        if (visited[x]->word == finish){
            cout << "Distance from start to finish: " << visited[x]->distance << '\n';
        }
    }

    cout << "Path from start to finish:\n";
    vector<Node *> path;
    for (int x = 0; x < visited.size(); x++){
        if (visited[x]->word == finish){
            path.push_back(visited[x]);
            break;
        }
    }
    Node * current = path[0];
    while(current->previous != 0){
        path.push_back(current->previous);
        current = current->previous;
    }
    // traverse this list backwards
    for (int x = path.size() - 1; x >= 0; x--){
        cout << path[x]->word << '\n';
    }
}

void findBridge(string start, string finish, vector<vector<string> > words){
    // first, let's make sure our two words aren't 'islands'
    vector<string> startFriends = findNeighbors(start, words);
    vector<string> endFriends = findNeighbors(finish, words);
    outputVector(startFriends);
    cout << "-----------\n";
    outputVector(endFriends);
}

int main(int argc, char** argv){
    cout << "Started.\n";
    clock_t timer = clock();
    string wordlistFile;
    string start;
    string finish;
    if (argc >= 3 && argc < 5){
        start = argv[1];
        finish = argv[2];
    } else {
        cout << "must input a start word and a finish word. Optionally input your own wordlist, otherwise the default will be used.\n";
        return 0;
    }
    if (argc == 4){
        wordlistFile = argv[3];
    } else {
        wordlistFile = "wordlist.txt";
    }

    // removing duplicates from our wordlist adds too much time overhead
    //  we'll just trust that our wordlist is alright
    vector<string> words = readWords(wordlistFile);

    // cout << "wordlist contains " << words.size() << " words.\n";

    if (verifyWord(start, words) && verifyWord(finish, words)){
        vector<vector<string> > splitList = wordsByLength(words);
        Dijkstra(start, finish, splitList, words.size());
    } else {
        // this can be optimized
        if (!verifyWord(start, words) && !verifyWord(finish, words)){
            cout << "start word and finish word not found in list\n";
        } else if (!verifyWord(start, words)){
            cout << "start word not found in list\n";
        } else {
            cout << "finish word not found in list\n";
        }
        return 0;
    }
    std::cout << "Complete. Took " << (float(clock () - timer)/CLOCKS_PER_SEC) << " seconds.\n";
    return 0;
}
