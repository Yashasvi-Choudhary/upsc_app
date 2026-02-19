-- MySQL dump 10.13  Distrib 8.0.39, for Win64 (x86_64)
--
-- Host: localhost    Database: upsc_app
-- ------------------------------------------------------
-- Server version	8.0.39

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `feedback`
--

DROP TABLE IF EXISTS `feedback`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `feedback` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `message` text NOT NULL,
  `submitted_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `feedback`
--

LOCK TABLES `feedback` WRITE;
/*!40000 ALTER TABLE `feedback` DISABLE KEYS */;
INSERT INTO `feedback` VALUES (1,'yashasvi choudhary','It is really helpful thank you','2025-05-27 13:29:15'),(2,'Diksha Patil','This app is really helpful and it helps me in all sections of my studies intruding current affairs, static GK ,pyqs paper, NCERT books everything is nice. Once again thank you','2025-05-27 13:55:43'),(3,'shivani','hello ','2025-05-27 14:43:53');
/*!40000 ALTER TABLE `feedback` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `syllabus`
--

DROP TABLE IF EXISTS `syllabus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `syllabus` (
  `id` int NOT NULL AUTO_INCREMENT,
  `exam_type` varchar(100) NOT NULL,
  `paper_type` varchar(100) NOT NULL,
  `year` int NOT NULL,
  `link` varchar(255) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `syllabus`
--

LOCK TABLES `syllabus` WRITE;
/*!40000 ALTER TABLE `syllabus` DISABLE KEYS */;
INSERT INTO `syllabus` VALUES (1,'Prelims','GS-I',2024,'/static/syllabus.pdf','2025-05-06 09:15:50'),(2,'Prelims','CSAT',2024,'/static/syllabus.pdf','2025-05-06 09:15:50'),(3,'Mains','GS-I',2024,'https://www.drishtiias.com/pdf/1743399249.pdf','2025-05-06 09:16:14'),(4,'Mains','GS-II',2024,'https://www.drishtiias.com/pdf/1742950409.pdf','2025-05-06 09:16:14'),(5,'Mains','GS-III',2024,'https://www.drishtiias.com/pdf/1742995283.pdf','2025-05-06 09:16:14'),(6,'Mains','GS-IV',2024,'https://www.drishtiias.com/pdf/1739674996.pdf','2025-05-06 09:16:14'),(7,'Mains','GS-I',2025,'/static/syllabus.pdf','2025-05-22 14:36:52');
/*!40000 ALTER TABLE `syllabus` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `upsc_papers`
--

DROP TABLE IF EXISTS `upsc_papers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `upsc_papers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `exam_type` varchar(50) DEFAULT NULL,
  `paper_type` varchar(100) DEFAULT NULL,
  `sub_paper_type` varchar(50) DEFAULT NULL,
  `year` int DEFAULT NULL,
  `pdf_link` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `upsc_papers`
--

LOCK TABLES `upsc_papers` WRITE;
/*!40000 ALTER TABLE `upsc_papers` DISABLE KEYS */;
INSERT INTO `upsc_papers` VALUES (1,'PRELIMS','GENERAL STUDIES (GS)',NULL,2024,'https://www.drishtiias.com/images/pdf/1718537625_upsc-pre-2024-GS-(B).pdf'),(2,'PRELIMS','GENERAL STUDIES (GS)',NULL,2023,'https://www.drishtiias.com/images/pdf/UPSC%202023%20Questions%20English.pdf'),(3,'PRELIMS','GENERAL STUDIES (GS)',NULL,2022,'https://www.drishtiias.com/images/pdf/GS%20Paper%202022%20(English)%20with%20logo.pdf'),(4,'PRELIMS','GENERAL STUDIES (GS)',NULL,2021,'https://www.drishtiias.com/images/pdf/New%20doc%20Oct%2010,%202021%2011.35%20(English%20).pdf'),(5,'PRELIMS','GENERAL STUDIES (GS)',NULL,2020,'https://www.drishtiias.com/images/pdf/UPSC_Prelims_Exam_2020_GS_Paper_I.pdf.pdf'),(6,'PRELIMS','CSAT',NULL,2024,'https://www.drishtiias.com/images/pdf/1718559311_CSE-2024%20Prelims%20CSAT%20Paper%20(B).pdf'),(7,'PRELIMS','CSAT',NULL,2023,'https://www.drishtiias.com/images/pdf/GENERAL_STUDIES_PAPER_II_CSAT_2023-1.pdf'),(8,'PRELIMS','CSAT',NULL,2022,'https://www.drishtiias.com/images/pdf/CSAT%20GENERAL%20STUDIES%20PAPER%20II%202022.pdf'),(9,'PRELIMS','CSAT',NULL,2021,'https://www.drishtiias.com/images/pdf/UPSC%20Prelims%20CSAT%202021%20Engilsh.pdf'),(10,'PRELIMS','CSAT',NULL,2020,'https://www.drishtiias.com/images/pdf/Prelims%20Question%20Paper-II%202019.pdf'),(11,'MAINS','GS-I',NULL,2024,'https://www.drishtiias.com/images/pdf/UPSC%20Mains%202024%20GS%20Paper%20I...pdf'),(12,'MAINS','GS-I',NULL,2023,'https://www.drishtiias.com/images/pdf/02%20UPSC%20GS%20Mains%20Paper_Final.pdf'),(13,'MAINS','GS-I',NULL,2022,'https://www.drishtiias.com/images/pdf/UPSC%20GS%20Mains%20Paper%20History%202022.pdf'),(14,'MAINS','GS-I',NULL,2021,'https://www.drishtiias.com/images/pdf/GS%20Paper-I%20(English).pdf'),(15,'MAINS','GS-I',NULL,2020,'https://www.sanskritiias.com/uploaded_files/pdf/Hindi_Compulsory.pdf'),(16,'MAINS','GS-II',NULL,2024,'https://www.drishtiias.com/images/pdf/02%20UPSC%202024%20Paper-II.pdf'),(17,'MAINS','GS-II',NULL,2023,'https://www.drishtiias.com/images/pdf/03%20UPSC%20GS%20Mains%20Paper_Final%20(Polity).pdf'),(18,'MAINS','GS-II',NULL,2022,'https://www.drishtiias.com/images/pdf/GS%20Mains%20Paper%20II%20(2022).pdf'),(19,'MAINS','GS-II',NULL,2021,'https://www.drishtiias.com/images/pdf/Gs%20paper%202%20(2021).pdf'),(20,'MAINS','GS-II',NULL,2020,'https://www.drishtiias.com/images/pdf/GS%20Mains%20Paper-II%20(2020).pdf'),(21,'MAINS','GS-III',NULL,2024,'https://www.drishtiias.com/images/pdf/03%20UPSC%202024%20Paper-III.pdf'),(22,'MAINS','GS-III',NULL,2023,'https://www.drishtiias.com/images/pdf/04%20UPSC%20GS%20Mains%20Paper_Final%201.pdf'),(23,'MAINS','GS-III',NULL,2022,'https://www.drishtiias.com/images/pdf/GS%20Mains%20Paper%20III%20(2022).pdf'),(24,'MAINS','GS-III',NULL,2021,'https://www.drishtiias.com/images/pdf/G.S%20Paper-III%20(2021).pdf'),(25,'MAINS','GS-III',NULL,2020,'https://www.drishtiias.com/images/pdf/GS%20Mains%20Paper-III%20(2020).pdf'),(26,'MAINS','GS-IV',NULL,2024,'https://www.drishtiias.com/images/pdf/05%20UPSC%202024%20Paper-IV_Final%201.pdf'),(27,'MAINS','GS-IV',NULL,2023,'https://www.drishtiias.com/images/pdf/05%20UPSC%20GS%20Mains%20Paper_Final%202.pdf'),(28,'MAINS','GS-IV',NULL,2022,'https://www.drishtiias.com/images/pdf/GS%20Mains%20Paper%20IV%20(2022).pdf'),(29,'MAINS','GS-IV',NULL,2021,'https://www.drishtiias.com/images/pdf/G.S%20Paper-4%20(2021).pdf'),(30,'MAINS','GS-IV',NULL,2020,'https://www.drishtiias.com/images/pdf/GS%20Mains%20Paper-IV%20(2020).pdf'),(31,'MAINS','ESSAY',NULL,2024,'https://www.drishtiias.com/images/pdf/UPSC%20Mains%202024%20Essay%20Paper...pdf'),(32,'MAINS','ESSAY',NULL,2023,'https://www.drishtiias.com/images/pdf/00%20UPSC%20GS%20Mains%20Paper%20Eassy%2015.09.2023.pdf'),(33,'MAINS','ESSAY',NULL,2022,'https://www.drishtiias.com/images/pdf/UPSC%20GS%20Mains%20Paper%20Eassy%202022.pdf'),(34,'MAINS','ESSAY',NULL,2021,'https://www.drishtiias.com/images/pdf/GS%20Mains%20Paper%20Essay%20(2021).pdf'),(35,'MAINS','ESSAY',NULL,2020,'https://www.drishtiias.com/images/pdf/GS%20Mains%20Paper%20Essay%20(2020).pdf'),(36,'MAINS','QUALIFYING PAPERS','HINDI',2024,'https://www.sanskritiias.com/uploaded_files/pdf/Hindi_Compulsory.pdf'),(37,'MAINS','QUALIFYING PAPERS','HINDI',2023,'https://www.sanskritiias.com/uploaded_files/pdf/QP-CSM-23-HINDI-COMPULSORY-290923.pdf'),(38,'MAINS','QUALIFYING PAPERS','HINDI',2022,'https://www.sanskritiias.com/uploaded_files/pdf/QP-CSM-22-HINDI-Compl.pdf'),(39,'MAINS','QUALIFYING PAPERS','HINDI',2021,'https://www.sanskritiias.com/uploaded_files/pdf/Compalsory-Hindi-2021.pdf'),(40,'MAINS','QUALIFYING PAPERS','HINDI',2020,'https://www.sanskritiias.com/uploaded_files/exam-paper/mains/2020/compulsory-hindi-2020.pdf'),(41,'MAINS','QUALIFYING PAPERS','ENGLISH',2024,'https://www.sanskritiias.com/uploaded_files/pdf/English_Compulsory.pdf'),(42,'MAINS','QUALIFYING PAPERS','ENGLISH',2023,'https://www.sanskritiias.com/uploaded_files/pdf/QP-CSM-23-ENGLISH-COMPULSORY-290923.pdf'),(43,'MAINS','QUALIFYING PAPERS','ENGLISH',2022,'https://www.sanskritiias.com/uploaded_files/pdf/QP-CSM-22-ENGLISH-Compl.pdf'),(44,'MAINS','QUALIFYING PAPERS','ENGLISH',2021,'https://www.sanskritiias.com/uploaded_files/exam-paper/mains/2021/compulsory-English-2021.pdf'),(45,'MAINS','QUALIFYING PAPERS','ENGLISH',2020,'https://www.sanskritiias.com/uploaded_files/pdf/QP-CSM-23-ENGLISH-COMPULSORY-290923.pdf');
/*!40000 ALTER TABLE `upsc_papers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(150) NOT NULL,
  `password` varchar(200) NOT NULL,
  `username` varchar(100) DEFAULT NULL,
  `session_token` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (2,'yashasvichoudhary@08gmail.com','scrypt:32768:8:1$A2gnUDphwtoTR85W$02a3752e51cdd4913c708ed6201a3d86e05723b6872d2497c5e4fc88967dc307665fceff6d983f74178cd400016a199b4eda6f7eea0787f191104ce2fadc13b9','Yashasvi  Choudhary',NULL),(9,'diksha123@gmail.com','scrypt:32768:8:1$zIm6xbedF61ZxlAX$a6a01f65bf480ec5eaed19ad5fa59b541ab3991b6e79b4bd08af2499dac9c78e677cbed06cfc0f52a91c82b52063bb6e50a75931c1a828b607e78bc94fb1f190','Diksha Patil',NULL),(10,'yashasvi123@gmail.com','scrypt:32768:8:1$3GCutJ1sqzvXRNzI$21d72cf2c0bd3d237e326cee3c4218a403dfa79e8491cfb34f4feaa23f69e27dc0d253e2a3eb7bb102f6b45716ce577b57da8b4fed76db72064c340281bbb32e','Yashasvi','6613f1dc-92bb-476a-995a-de2b3d861c4c'),(12,'dikshapatil@gmail.com','scrypt:32768:8:1$XS1xMcVs68ihrhmN$c2c8b479c2da8703af3521550b93ddeccdaef590f0a43ff1916333c866ee189c9957caddda35b7acf649d40c033ac5d769ffa4ef5ca102db2d7008df8ff67e02','diksha','e4e223a9-9297-4955-a8e9-8b242413d38f'),(13,'anaya01@gmail.com','scrypt:32768:8:1$33rjLlo1FnXUSKCo$abc5e0bfbeb0ff49c0366021a2032548658c6ec544f751c52437500bb1bd171bdc6300663708c2da8253f740f3de641089006a96a13c327390116af3df09b65b','Anaya','3afbf130-113a-48f2-b92a-6a6a2948142b');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-19 23:41:43
