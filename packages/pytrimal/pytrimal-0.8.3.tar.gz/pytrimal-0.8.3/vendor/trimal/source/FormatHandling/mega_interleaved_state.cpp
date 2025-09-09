/* *****************************************************************************

    trimAl v2.0: a tool for automated alignment trimming in large-scale
                 phylogenetics analyses.

    readAl v2.0: a tool for automated alignment conversion among different
                 formats.

    2009-2019
        Fernandez-Rodriguez V.  (victor.fernandez@bsc.es)
        Capella-Gutierrez S.    (salvador.capella@bsc.es)
        Gabaldon, T.            (tgabaldon@crg.es)

    This file is part of trimAl/readAl.

    trimAl/readAl are free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, the last available version.

    trimAl/readAl are distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with trimAl/readAl. If not, see <http://www.gnu.org/licenses/>.

***************************************************************************** */

#include "FormatHandling/mega_interleaved_state.h"

#include "FormatHandling/FormatManager.h"
#include "defines.h"
#include "utils.h"

namespace FormatHandling {
int mega_interleaved_state::CheckAlignment(std::istream* origin)
{
    origin->seekg(0);
    origin->clear();
    
    char c, *firstWord = nullptr, *line = nullptr;
    int blocks = 0;
    std::string buffer;
    
    /* Read first valid line in a safer way */
    do {
        line = utils::readLine(*origin, buffer);
    } while ((line == nullptr) && (!origin->eof()));

    /* If the file end is reached without a valid line, warn about it */
    if (origin->eof())
    {
        return 0;
    }

    /* Otherwise, split line */
    firstWord = strtok(line, OTHDELIMITERS);

        /* Mega Format */
    if((!strcmp(firstWord, "#MEGA")) ||
       (!strcmp(firstWord, "#mega"))) {

        /* Determine specific mega format: sequential or interleaved.
         * Counting the number of blocks (set of lines starting by "#") in
         * the input file. */
        blocks = 0;
        do {
            origin->read(&c, 1);
        } while((c != '#') && (!origin->eof()));

        do {
            while((c != '\n') && (!origin->eof()))
                origin->read(&c, 1);
            origin->read(&c, 1);
            if(c == '#')
                blocks++;
        } while((c != '\n') && (!origin->eof()));

        /* MEGA Sequential (22) or Interleaved (21) */
        return (!blocks) ? 0 : 1;
    }
    return 0;
}

Alignment* mega_interleaved_state::LoadAlignment(std::istream& file)
{
    Alignment * alig = new Alignment();
   /* MEGA interleaved file format parser */

    char *frag = nullptr, *str = nullptr, *line = nullptr;
    int i, firstBlock = true;
    std::string buffer;
    
    /* Skip first valid line */
    do {
        line = utils::readLine(file, buffer);
    } while ((line == nullptr) && (!file.eof()));

    /* If the file end is reached without a valid line, warn about it */
    if (file.eof())
        return nullptr;

    /* Try to get input alignment information */
    while(!file.eof()) {

        /* Read a new line in a safe way */
        line = utils::readLine(file, buffer);
        if (line == nullptr)
            continue;

        /* If a sequence name flag is found, go out from getting information loop */
        if(!strncmp(line, "#", 1))
            break;

        /* Create a local copy from input line */
        frag = new char[strlen(line) + 1];
        strcpy(frag, line);

        /* Split input line copy into pieces and analize it
         * looking for specific labels */
        str = strtok(frag, "!: ");
        for(i = 0; i < (int) strlen(str); i++)
            str[i] = toupper(str[i]);

        /* If TITLE label is found, replace previously stored information with
         * this info */
        if(!strcmp(str, "TITLE")) {
            alig->filename.clear();
            if(strncmp(line, "!", 1))
                alig->filename += "!";
            alig->filename += line;
        }
            /* If FORMAT label is found, try to get some details from input file */
        else if(!strcmp(str, "FORMAT"))
             alig->alignmentInfo.append(line, strlen(line));

        /* Destroy previously allocated memory */
        delete [] frag;
    }

    /* Count how many sequences are in input file */
    while(!file.eof()) {

        /* If a sequence name flag has been detected, increase counter */
        if(!strncmp(line, "#", 1))
            alig->numberOfSequences++;

        /* Read lines in a safe way */
        line = utils::readLine(file, buffer);

        /* If a blank line is detected means first block of sequences is over */
        /* Then, break counting sequences loop */
        if (line == nullptr)
            break;
    }

    /* Finish to preprocess the input file. */
    file.clear();
    file.seekg(0);

    /* Allocate memory */
    alig->seqsName  = new std::string[alig->numberOfSequences];
    alig->sequences = new std::string[alig->numberOfSequences];

    /* Skip first line */
    line = utils::readLine(file, buffer);

    /* Skip lines until first # flag is reached */
    while(!file.eof()) {

        /* Read line in a safer way */
        line = utils::readLine(file, buffer);

        /* Determine whether a # flag has been found in current std::string */
        if (line != nullptr)
            if(!strncmp(line, "#", 1))
                break;
    }

    /* Read sequences and get from first block, the sequences names */
    i = 0;
    firstBlock = true;

    while(!file.eof()) {

        if (line == nullptr) {
            /* Read line in a safer way */
            line = utils::readLine(file, buffer);
            continue;
        }

        if (!strncmp(line, "!", 1)) {
            /* Deallocate memory and read a new line */
            line = utils::readLine(file, buffer);
            continue;
        }

        /* Trim lines from any kind of comments and split it */
        frag = utils::trimLine(line);
        str = strtok(frag, " #\n");

        /* Check whether a line fragment is valid or not */
        if (str == nullptr)
            continue;

        /* Store sequences names if firstBlock flag is TRUE */
        if(firstBlock)
            alig->seqsName[i].append(str, strlen(str));

        /* Store sequence */
        str = strtok(nullptr, " \n");
        while(str != nullptr) {
            alig->sequences[i].append(str, strlen(str));
            str = strtok(nullptr, " \n");
        }

        /* Deallocate previously used dynamic memory */
        delete [] frag;

        /* Read line in a safer way */
        line = utils::readLine(file, buffer);

        i = (i + 1) % alig->numberOfSequences;
        if (i == 0)
            firstBlock = false;
    }

    /* Check the matrix's content */
    alig->fillMatrices(true);
    alig->originalNumberOfSequences = alig -> numberOfSequences;
    alig->originalNumberOfResidues = alig -> numberOfResidues;
    return alig;
}

bool mega_interleaved_state::SaveAlignment(const Alignment &alignment, std::ostream *output)
{
    return false;
}

bool mega_interleaved_state::RecognizeOutputFormat(const std::string &FormatName)
{
    return false;
}
}
