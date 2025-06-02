-- MariaDB dump 10.19  Distrib 10.5.23-MariaDB, for debian-linux-gnu (aarch64)
--
-- Host: localhost    Database: NearonProjectDB
-- ------------------------------------------------------
-- Server version	10.5.23-MariaDB-0+deb11u1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `actuatorGroupDB`
--

DROP TABLE IF EXISTS `actuatorGroupDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `actuatorGroupDB` (
  `id` varchar(10) NOT NULL,
  `number` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `intervals` int(11) NOT NULL,
  `unit` tinyint(1) NOT NULL,
  `service_id` int(11) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `number` (`number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `actuatorGroupDB`
--

LOCK TABLES `actuatorGroupDB` WRITE;
/*!40000 ALTER TABLE `actuatorGroupDB` DISABLE KEYS */;
INSERT INTO `actuatorGroupDB` VALUES ('PAG-O59DK',2,'CBU',2,1,42,'2025-04-29 18:43:29','2025-04-29 21:25:57'),('PAG-OJA3Z',1,'RTU',1,1,41,'2025-04-29 16:54:29','2025-04-29 18:43:38');
/*!40000 ALTER TABLE `actuatorGroupDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `actuatorListDB`
--

DROP TABLE IF EXISTS `actuatorListDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `actuatorListDB` (
  `id` varchar(10) NOT NULL,
  `actuator_group_id` varchar(10) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `actuator_custom_id` varchar(50) DEFAULT NULL,
  `server_value` varchar(50) DEFAULT NULL,
  `server_sync_at` datetime DEFAULT NULL,
  `last_server_value` varchar(50) DEFAULT NULL,
  `last_server_sync_at` datetime DEFAULT NULL,
  `last_action` tinyint(1) DEFAULT NULL,
  `last_action_value` varchar(50) DEFAULT NULL,
  `last_action_at` datetime DEFAULT NULL,
  `schedule` tinyint(1) DEFAULT NULL,
  `type_actuator` tinyint(1) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `actuator_custom_id` (`actuator_custom_id`),
  KEY `fk_actuator_group` (`actuator_group_id`),
  CONSTRAINT `fk_actuator_group` FOREIGN KEY (`actuator_group_id`) REFERENCES `actuatorGroupDB` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `actuatorListDB`
--

LOCK TABLES `actuatorListDB` WRITE;
/*!40000 ALTER TABLE `actuatorListDB` DISABLE KEYS */;
INSERT INTO `actuatorListDB` VALUES ('PAL-BIDX9','PAG-OJA3Z','Remote Motor Start - RTU 1','motorStartRtu1',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,'2025-06-01 22:54:17','2025-06-02 00:02:41'),('PAL-QDXFH','PAG-OJA3Z','Remote Motor Start - RTU 2','remoteStartRtu2',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,'2025-06-01 23:51:47','2025-06-02 00:02:50'),('PAL-Y7MDW','PAG-OJA3Z','Remote Motor Stop - RTU 1','motorStopRtu1','1','2025-06-01 22:21:16',NULL,NULL,NULL,NULL,NULL,0,0,'2025-04-29 17:11:34','2025-06-02 00:02:35');
/*!40000 ALTER TABLE `actuatorListDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `actuatorParameterGroupDB`
--

DROP TABLE IF EXISTS `actuatorParameterGroupDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `actuatorParameterGroupDB` (
  `id` varchar(10) NOT NULL,
  `actuator_group_id` varchar(10) NOT NULL,
  `name` varchar(100) NOT NULL,
  `parameter` varchar(100) NOT NULL,
  `value` varchar(100) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `fk_actuator_group2` (`actuator_group_id`),
  CONSTRAINT `fk_actuator_group2` FOREIGN KEY (`actuator_group_id`) REFERENCES `actuatorGroupDB` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `actuatorParameterGroupDB`
--

LOCK TABLES `actuatorParameterGroupDB` WRITE;
/*!40000 ALTER TABLE `actuatorParameterGroupDB` DISABLE KEYS */;
INSERT INTO `actuatorParameterGroupDB` VALUES ('PAPG-9GP7K','PAG-OJA3Z','Slave ID RTU 1','slave_id1','1','2025-06-01 22:50:02','2025-06-01 22:50:02'),('PAPG-SSACN','PAG-OJA3Z','Baudrate','baudrate','9600','2025-06-01 22:49:43','2025-06-01 22:49:43'),('PAPG-SU183','PAG-OJA3Z','Slave ID 2','slave_id2','2','2025-06-01 23:51:10','2025-06-01 23:51:10'),('PAPG-VDRD0','PAG-OJA3Z','Port','port','1','2025-06-01 22:49:28','2025-06-01 22:49:28');
/*!40000 ALTER TABLE `actuatorParameterGroupDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `actuatorParameterListDB`
--

DROP TABLE IF EXISTS `actuatorParameterListDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `actuatorParameterListDB` (
  `id` varchar(10) NOT NULL,
  `actuator_list_id` varchar(10) NOT NULL,
  `name` varchar(100) NOT NULL,
  `parameter` varchar(100) NOT NULL,
  `value` varchar(100) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `fk_actuator_list` (`actuator_list_id`),
  CONSTRAINT `fk_actuator_list` FOREIGN KEY (`actuator_list_id`) REFERENCES `actuatorListDB` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `actuatorParameterListDB`
--

LOCK TABLES `actuatorParameterListDB` WRITE;
/*!40000 ALTER TABLE `actuatorParameterListDB` DISABLE KEYS */;
INSERT INTO `actuatorParameterListDB` VALUES ('PAPL-E4YWC','PAL-Y7MDW','Address','address','1','2025-06-01 23:13:24','2025-06-01 23:20:26'),('PAPL-QFYR6','PAL-QDXFH','Address','address','3','2025-06-01 23:51:56','2025-06-01 23:51:56'),('PAPL-V6S1I','PAL-BIDX9','Address','address','3','2025-06-01 23:13:51','2025-06-01 23:13:51');
/*!40000 ALTER TABLE `actuatorParameterListDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `actuatorScheduleDB`
--

DROP TABLE IF EXISTS `actuatorScheduleDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `actuatorScheduleDB` (
  `id` varchar(10) NOT NULL,
  `actuator_list_id` varchar(10) NOT NULL,
  `day` varchar(20) NOT NULL,
  `time` time NOT NULL,
  `value` varchar(50) NOT NULL,
  `state` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `FK_ACTUATOR_SCHEDULE_LIST_idx` (`actuator_list_id`),
  CONSTRAINT `FK_ACTUATOR_SCHEDULE_LIST` FOREIGN KEY (`actuator_list_id`) REFERENCES `actuatorListDB` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `actuatorScheduleDB`
--

LOCK TABLES `actuatorScheduleDB` WRITE;
/*!40000 ALTER TABLE `actuatorScheduleDB` DISABLE KEYS */;
/*!40000 ALTER TABLE `actuatorScheduleDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `calibrateFormulaDB`
--

DROP TABLE IF EXISTS `calibrateFormulaDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `calibrateFormulaDB` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `sample` int(11) NOT NULL,
  `koef_a` varchar(30) DEFAULT NULL,
  `koef_b` varchar(30) DEFAULT NULL,
  `calculate_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `calibrateFormulaDB`
--

LOCK TABLES `calibrateFormulaDB` WRITE;
/*!40000 ALTER TABLE `calibrateFormulaDB` DISABLE KEYS */;
INSERT INTO `calibrateFormulaDB` VALUES (1,'Regresi Arus',36,'0.7676','-0.0605','2024-12-11 23:45:27'),(5,'Regresi Arus 2',37,'0.766','-0.0695','2024-06-22 17:20:29');
/*!40000 ALTER TABLE `calibrateFormulaDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `calibrateSampleDB`
--

DROP TABLE IF EXISTS `calibrateSampleDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `calibrateSampleDB` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `formula_id` bigint(20) NOT NULL,
  `value_sample` varchar(30) NOT NULL,
  `value_reference` varchar(30) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `formula_sample` (`formula_id`)
) ENGINE=InnoDB AUTO_INCREMENT=89 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `calibrateSampleDB`
--

LOCK TABLES `calibrateSampleDB` WRITE;
/*!40000 ALTER TABLE `calibrateSampleDB` DISABLE KEYS */;
INSERT INTO `calibrateSampleDB` VALUES (2,1,'0.8','0.57'),(4,1,'1.05','0.75'),(5,1,'1.16','0.84'),(6,1,'1.23','0.89'),(14,1,'1.28','0.93'),(15,1,'1.56','1.12'),(16,1,'1.84','1.34'),(17,1,'2.05','1.51'),(18,1,'2.18','1.63'),(19,1,'2.31','1.69'),(20,1,'2.62','1.94'),(21,1,'2.84','2.11'),(22,1,'3.03','2.26'),(23,1,'3.37','2.52'),(24,1,'4.5','3.42'),(25,1,'6.06','4.59'),(26,1,'6.36','4.82'),(27,1,'7.02','5.33'),(28,1,'7.17','5.44'),(29,1,'7.52','5.71'),(30,1,'7.88','5.99'),(31,1,'8.13','6.18'),(32,1,'8.17','6.21'),(33,1,'8.65','6.58'),(34,1,'8.93','6.79'),(35,1,'9.21','7.01'),(36,1,'9.22','7.02'),(37,1,'9.65','7.35'),(38,1,'10.08','7.68'),(39,1,'10.23','7.79'),(40,1,'10.48','7.98'),(41,1,'10.72','8.17'),(42,1,'11.10','8.46'),(43,1,'11.53','8.79'),(44,1,'12.10','9.23'),(45,1,'12.39','9.45'),(48,5,'0.79','0.57'),(49,5,'1.04','0.76'),(50,5,'1.12','0.85'),(51,5,'1.24','0.92'),(52,5,'1.3','0.94'),(53,5,'1.55','1.11'),(54,5,'1.69','1.32'),(55,5,'1.86','1.39'),(56,5,'2.04','1.49'),(57,5,'2.18','1.6'),(58,5,'2.3','1.68'),(59,5,'2.62','1.91'),(60,5,'2.85','2.09'),(61,5,'3.04','2.23'),(62,5,'3.36','2.49'),(63,5,'4.51','3.44'),(64,5,'6.19','4.6'),(65,5,'6.31','4.73'),(66,5,'7.03','5.2'),(67,5,'7.20','5.43'),(68,5,'7.57','5.61'),(69,5,'7.97','5.96'),(70,5,'8.21','6.16'),(71,5,'8.40','6.33'),(72,5,'8.58','6.46'),(73,5,'9.12','6.85'),(74,5,'9.20','7.05'),(75,5,'9.52','7.22'),(76,5,'9.62','7.32'),(77,5,'10.18','7.67'),(78,5,'10.33','7.74'),(79,5,'10.55','8.1'),(80,5,'10.59','8.04'),(81,5,'11.21','8.52'),(82,5,'11.53','8.85'),(83,5,'11.88','9.18'),(84,5,'12.29','9.47');
/*!40000 ALTER TABLE `calibrateSampleDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `deviceSettingDB`
--

DROP TABLE IF EXISTS `deviceSettingDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `deviceSettingDB` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(10) NOT NULL,
  `value` varchar(100) NOT NULL,
  `updatedAt` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `deviceSettingDB`
--

LOCK TABLES `deviceSettingDB` WRITE;
/*!40000 ALTER TABLE `deviceSettingDB` DISABLE KEYS */;
INSERT INTO `deviceSettingDB` VALUES (1,'uid','25b6148d45d1453ca7adf412ff151ac8','2025-04-29 21:37:58'),(2,'name','Nearon IoT - SLB','2025-04-29 21:37:50'),(3,'version','1.0.0','2024-04-17 16:09:44');
/*!40000 ALTER TABLE `deviceSettingDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `environmentDeviceDB`
--

DROP TABLE IF EXISTS `environmentDeviceDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `environmentDeviceDB` (
  `id` varchar(50) NOT NULL,
  `number` int(11) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `method` varchar(10) DEFAULT NULL,
  `ip` varchar(255) DEFAULT NULL,
  `modbus_id` varchar(10) DEFAULT NULL,
  `port1` int(11) DEFAULT NULL,
  `port2` int(11) DEFAULT NULL,
  `port3` int(11) DEFAULT NULL,
  `port4` int(11) DEFAULT NULL,
  `port5` int(11) DEFAULT NULL,
  `port6` int(11) DEFAULT NULL,
  `port7` int(11) DEFAULT NULL,
  `port8` int(11) DEFAULT NULL,
  `state` tinyint(4) DEFAULT NULL,
  `createdAt` datetime DEFAULT NULL,
  `updatedAt` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `number` (`number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `environmentDeviceDB`
--

LOCK TABLES `environmentDeviceDB` WRITE;
/*!40000 ALTER TABLE `environmentDeviceDB` DISABLE KEYS */;
INSERT INTO `environmentDeviceDB` VALUES ('EED-VZOUQ',1,'Extension Device','0','10.19.52.89','0',2,2,0,0,0,0,0,0,1,'2025-03-12 15:44:40','2025-04-28 08:43:20');
/*!40000 ALTER TABLE `environmentDeviceDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `environmentMasterParameterDB`
--

DROP TABLE IF EXISTS `environmentMasterParameterDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `environmentMasterParameterDB` (
  `id` varchar(50) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `parameterCode` varchar(255) DEFAULT NULL,
  `createdAt` datetime DEFAULT current_timestamp(),
  `updatedAt` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `environmentMasterParameterDB`
--

LOCK TABLES `environmentMasterParameterDB` WRITE;
/*!40000 ALTER TABLE `environmentMasterParameterDB` DISABLE KEYS */;
INSERT INTO `environmentMasterParameterDB` VALUES ('EEMP-6Ipe7','Endpoint','endpoint','2024-09-24 11:25:25','2024-09-30 03:34:45'),('EEMP-CdHN0','waterSplash','codeString','2024-10-02 12:06:08','2024-10-02 05:06:08'),('EEMP-qrnVM','IP Address','ip','2024-09-24 11:32:56','2024-09-30 03:34:34'),('EEMP-viTDz','Device Status','device','2024-09-24 11:31:43','2024-09-30 03:35:57');
/*!40000 ALTER TABLE `environmentMasterParameterDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `environmentMasterSensorDB`
--

DROP TABLE IF EXISTS `environmentMasterSensorDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `environmentMasterSensorDB` (
  `id` varchar(50) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `sensorId` varchar(255) DEFAULT NULL,
  `createdAt` datetime DEFAULT current_timestamp(),
  `updatedAt` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `environmentMasterSensorDB`
--

LOCK TABLES `environmentMasterSensorDB` WRITE;
/*!40000 ALTER TABLE `environmentMasterSensorDB` DISABLE KEYS */;
INSERT INTO `environmentMasterSensorDB` VALUES ('EEMS-BpAoR','Temperature Port 1','tempP1','2024-09-24 10:34:41','2024-09-30 03:31:37'),('EEMS-c6B7f','Humidity Port 1','humidP1','2024-09-24 10:48:01','2024-09-30 03:31:48'),('EEMS-EtDdv','Water Cannon','waterCannon','2024-10-02 12:05:44','2024-10-02 05:05:44'),('EEMS-MMnXN','Humidity Port 2','humidP2','2024-09-30 10:32:10','2024-09-30 03:32:10'),('EEMS-nzEi6','Smoke Detector','inputP5','2024-09-30 10:33:10','2024-09-30 03:33:10'),('EEMS-UT6mc','Door State','inputP4','2024-09-30 10:32:58','2024-09-30 03:32:58'),('EEMS-vwooB','Temperature Port 2','tempP2','2024-09-30 10:31:57','2024-09-30 03:31:57'),('EEMS-wuXWY','Water Leak','inputP6','2024-09-30 10:33:21','2024-09-30 03:33:21');
/*!40000 ALTER TABLE `environmentMasterSensorDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `featureSettingDB`
--

DROP TABLE IF EXISTS `featureSettingDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `featureSettingDB` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `value` varchar(2) NOT NULL,
  `updatedAt` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `featureSettingDB`
--

LOCK TABLES `featureSettingDB` WRITE;
/*!40000 ALTER TABLE `featureSettingDB` DISABLE KEYS */;
INSERT INTO `featureSettingDB` VALUES (1,'routineMonitor','0','2025-04-29 09:52:46'),(2,'bufferMonitor','0','2025-04-29 09:52:46'),(3,'bufferMonitorInterval','10','2025-04-29 10:14:46'),(4,'bufferMonitorUnit','1','2024-06-06 07:31:26'),(5,'alarmMonitor','0','2025-04-29 09:52:46'),(6,'alarmMonitorInterval','5','2024-09-05 21:11:18'),(7,'alarmMonitorUnit','1','2024-06-05 11:41:43'),(8,'notification','0','2025-04-29 09:54:22'),(9,'notificationInterval','5','2025-04-29 10:14:35'),(10,'notificationUnit','1','2024-06-11 13:43:39'),(11,'notificationSensorWeb','1','2024-04-23 16:25:04'),(12,'notificationSensorWA','1','2024-06-03 09:53:42'),(13,'notificationSensorEmail','1','2024-04-23 11:30:34'),(14,'notificationSensorTelegram','1','2024-06-03 09:53:42'),(15,'notificationActuatorWeb','1','2024-05-26 17:45:45'),(16,'notificationActuatorWA','1','2024-06-16 11:19:08'),(17,'notificationActuatorEmail','1','2024-06-16 11:19:08'),(18,'notificationActuatorTelegram','1','2024-04-23 16:25:04'),(19,'notificationNodeWeb','1','2024-04-23 11:30:34'),(20,'notificationNodeWA','1','2024-04-23 16:25:04'),(21,'notificationNodeEmail','1','2024-06-03 09:53:42'),(22,'notificationNodeTelegram','1','2024-04-23 11:30:34'),(23,'synchronize','1','2025-04-29 21:28:48'),(24,'synchronizeInterval','5','2024-06-03 14:00:56'),(25,'synchronizeUnit','1','2024-04-23 16:32:41'),(26,'syncSensor','0','2025-04-29 21:28:48'),(27,'syncActuator','1','2024-12-11 22:40:47'),(28,'syncNode','0','2025-04-29 21:28:48'),(29,'log','0','2025-04-28 15:14:34'),(30,'logInterval','0','2024-03-25 14:13:15'),(31,'logUnit','0','2024-03-25 14:13:15'),(32,'durationStorageLog','8','2025-01-10 23:10:29'),(33,'durationStorageLogState','1','2025-01-10 23:10:29'),(34,'backupMonthlyLog','1','2025-01-10 23:10:29');
/*!40000 ALTER TABLE `featureSettingDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `intervalRoutineLogDB`
--

DROP TABLE IF EXISTS `intervalRoutineLogDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `intervalRoutineLogDB` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `interval` varchar(5) NOT NULL,
  `unit` varchar(30) NOT NULL,
  `createdAt` datetime NOT NULL DEFAULT current_timestamp(),
  `updatedAt` datetime NOT NULL DEFAULT current_timestamp(),
  `state` varchar(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `intervalRoutineLogDB`
--

LOCK TABLES `intervalRoutineLogDB` WRITE;
/*!40000 ALTER TABLE `intervalRoutineLogDB` DISABLE KEYS */;
INSERT INTO `intervalRoutineLogDB` VALUES (1,'60','1','2024-04-23 13:56:21','2024-04-23 13:56:21','1');
/*!40000 ALTER TABLE `intervalRoutineLogDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `intervalRoutineMonitorDB`
--

DROP TABLE IF EXISTS `intervalRoutineMonitorDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `intervalRoutineMonitorDB` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `interval` varchar(5) NOT NULL,
  `unit` varchar(30) NOT NULL,
  `createdAt` datetime NOT NULL DEFAULT current_timestamp(),
  `updatedAt` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `state` varchar(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `intervalRoutineMonitorDB`
--

LOCK TABLES `intervalRoutineMonitorDB` WRITE;
/*!40000 ALTER TABLE `intervalRoutineMonitorDB` DISABLE KEYS */;
INSERT INTO `intervalRoutineMonitorDB` VALUES (1,'60','1','2024-04-23 13:56:02','2025-03-21 11:25:43','1');
/*!40000 ALTER TABLE `intervalRoutineMonitorDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `logActuatorDB`
--

DROP TABLE IF EXISTS `logActuatorDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `logActuatorDB` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `actuator_list_id` varchar(10) NOT NULL,
  `value` varchar(50) NOT NULL,
  `action` tinyint(1) NOT NULL,
  `action_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `FK_ACTUATOR_LOG_LIST_idx` (`actuator_list_id`),
  CONSTRAINT `FK_ACTUATOR_LOG_LIST` FOREIGN KEY (`actuator_list_id`) REFERENCES `actuatorListDB` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `logActuatorDB`
--

LOCK TABLES `logActuatorDB` WRITE;
/*!40000 ALTER TABLE `logActuatorDB` DISABLE KEYS */;
/*!40000 ALTER TABLE `logActuatorDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `logAlarmDB`
--

DROP TABLE IF EXISTS `logAlarmDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `logAlarmDB` (
  `id` varchar(10) NOT NULL,
  `sensor_id` varchar(50) DEFAULT NULL,
  `value` varchar(200) NOT NULL,
  `tipe` int(11) NOT NULL,
  `count` int(11) NOT NULL,
  `count_time` int(11) NOT NULL,
  `tolerance` int(11) NOT NULL,
  `first_alarm` datetime NOT NULL,
  `last_alarm` datetime DEFAULT NULL,
  `flag` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `fk_logAlarm_sensor_id` (`sensor_id`),
  CONSTRAINT `fk_logAlarm_sensor_id` FOREIGN KEY (`sensor_id`) REFERENCES `sensorListDB` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `logAlarmDB`
--

LOCK TABLES `logAlarmDB` WRITE;
/*!40000 ALTER TABLE `logAlarmDB` DISABLE KEYS */;
INSERT INTO `logAlarmDB` VALUES ('ERR-95HEX','PLS-EKWYS','0.0',4,8457,10556,300,'2025-04-29 10:44:32','2025-04-29 10:49:35',1),('ERR-EDQP3','PLS-DRG90','0.0',4,8457,10556,300,'2025-04-29 10:44:32','2025-04-29 10:49:35',1),('ERR-EM05J','PLS-FUJUG','0.0',4,8457,10557,300,'2025-04-29 10:44:32','2025-04-29 10:49:35',1),('ERR-GK410','PLS-EA12A','0.0',4,8457,10556,300,'2025-04-29 10:44:32','2025-04-29 10:49:35',1),('ERR-I25DN','PLS-UOSFI','-1',4,4670,10549,300,'2025-04-29 10:44:31','2025-04-29 10:49:34',1),('ERR-Q81PK','PLS-11BUR','-1',4,4670,10549,300,'2025-04-29 10:44:31','2025-04-29 10:49:34',1),('ERR-WP663','PLS-IPF33','0.0',4,8457,10556,300,'2025-04-29 10:44:32','2025-04-29 10:49:35',1);
/*!40000 ALTER TABLE `logAlarmDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `logErrorDB`
--

DROP TABLE IF EXISTS `logErrorDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `logErrorDB` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `service` varchar(50) NOT NULL,
  `error` varchar(1000) NOT NULL,
  `file` varchar(100) NOT NULL,
  `line` varchar(50) NOT NULL,
  `timestamp` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `logErrorDB`
--

LOCK TABLES `logErrorDB` WRITE;
/*!40000 ALTER TABLE `logErrorDB` DISABLE KEYS */;
INSERT INTO `logErrorDB` VALUES (1,'Actuator 1','KeyError (\'actuator_custom_id\')','/home/connex/project/actuator/actuator1.py','69','2025-06-01 22:26:54');
/*!40000 ALTER TABLE `logErrorDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `logMonitoringDB`
--

DROP TABLE IF EXISTS `logMonitoringDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `logMonitoringDB` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `data` varchar(10000) DEFAULT NULL,
  `state` varchar(5) NOT NULL,
  `buffer` tinyint(1) NOT NULL,
  `timestamp` datetime NOT NULL,
  `tipe` int(11) NOT NULL,
  `attempt` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `logMonitoringDB`
--

LOCK TABLES `logMonitoringDB` WRITE;
/*!40000 ALTER TABLE `logMonitoringDB` DISABLE KEYS */;
/*!40000 ALTER TABLE `logMonitoringDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `logNotifDB`
--

DROP TABLE IF EXISTS `logNotifDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `logNotifDB` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(10) NOT NULL,
  `sensor` varchar(50) NOT NULL,
  `conditions` varchar(50) NOT NULL,
  `notif` varchar(10) NOT NULL,
  `subject` varchar(100) NOT NULL,
  `message` varchar(10000) NOT NULL,
  `state` varchar(15) NOT NULL,
  `create_time` datetime NOT NULL,
  `send_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `logNotifDB`
--

LOCK TABLES `logNotifDB` WRITE;
/*!40000 ALTER TABLE `logNotifDB` DISABLE KEYS */;
/*!40000 ALTER TABLE `logNotifDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `logSensorDB`
--

DROP TABLE IF EXISTS `logSensorDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `logSensorDB` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sensor_id` varchar(50) DEFAULT NULL,
  `data` varchar(200) NOT NULL,
  `timestamp` datetime NOT NULL,
  `tipe` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_logSensor_sensor_id` (`sensor_id`),
  CONSTRAINT `fk_logSensor_sensor_id` FOREIGN KEY (`sensor_id`) REFERENCES `sensorListDB` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `logSensorDB`
--

LOCK TABLES `logSensorDB` WRITE;
/*!40000 ALTER TABLE `logSensorDB` DISABLE KEYS */;
/*!40000 ALTER TABLE `logSensorDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `logToleranceAlarmDB`
--

DROP TABLE IF EXISTS `logToleranceAlarmDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `logToleranceAlarmDB` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `value` varchar(200) NOT NULL,
  `timestamp` datetime NOT NULL,
  `alarmId` varchar(10) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=518 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `logToleranceAlarmDB`
--

LOCK TABLES `logToleranceAlarmDB` WRITE;
/*!40000 ALTER TABLE `logToleranceAlarmDB` DISABLE KEYS */;
INSERT INTO `logToleranceAlarmDB` VALUES (173,'0.0','2025-04-29 10:44:38','ERR-95HEX'),(174,'0.0','2025-04-29 10:44:38','ERR-GK410'),(175,'0.0','2025-04-29 10:44:38','ERR-EDQP3'),(176,'0.0','2025-04-29 10:44:38','ERR-WP663'),(177,'0.0','2025-04-29 10:44:38','ERR-EM05J'),(178,'-1','2025-04-29 10:44:41','ERR-I25DN'),(179,'-1','2025-04-29 10:44:41','ERR-Q81PK'),(180,'0.0','2025-04-29 10:44:43','ERR-95HEX'),(181,'0.0','2025-04-29 10:44:43','ERR-GK410'),(182,'0.0','2025-04-29 10:44:43','ERR-EDQP3'),(183,'0.0','2025-04-29 10:44:43','ERR-WP663'),(184,'0.0','2025-04-29 10:44:43','ERR-EM05J'),(185,'0.0','2025-04-29 10:44:48','ERR-95HEX'),(186,'0.0','2025-04-29 10:44:48','ERR-GK410'),(187,'0.0','2025-04-29 10:44:48','ERR-EDQP3'),(188,'0.0','2025-04-29 10:44:48','ERR-WP663'),(189,'0.0','2025-04-29 10:44:48','ERR-EM05J'),(190,'-1','2025-04-29 10:44:52','ERR-I25DN'),(191,'-1','2025-04-29 10:44:52','ERR-Q81PK'),(192,'0.0','2025-04-29 10:44:54','ERR-95HEX'),(193,'0.0','2025-04-29 10:44:54','ERR-GK410'),(194,'0.0','2025-04-29 10:44:54','ERR-EDQP3'),(195,'0.0','2025-04-29 10:44:54','ERR-WP663'),(196,'0.0','2025-04-29 10:44:54','ERR-EM05J'),(197,'0.0','2025-04-29 10:44:59','ERR-95HEX'),(198,'0.0','2025-04-29 10:44:59','ERR-GK410'),(199,'0.0','2025-04-29 10:44:59','ERR-EDQP3'),(200,'0.0','2025-04-29 10:44:59','ERR-WP663'),(201,'0.0','2025-04-29 10:44:59','ERR-EM05J'),(202,'-1','2025-04-29 10:45:02','ERR-I25DN'),(203,'-1','2025-04-29 10:45:02','ERR-Q81PK'),(204,'0.0','2025-04-29 10:45:04','ERR-95HEX'),(205,'0.0','2025-04-29 10:45:04','ERR-GK410'),(206,'0.0','2025-04-29 10:45:04','ERR-EDQP3'),(207,'0.0','2025-04-29 10:45:04','ERR-WP663'),(208,'0.0','2025-04-29 10:45:04','ERR-EM05J'),(209,'0.0','2025-04-29 10:45:10','ERR-95HEX'),(210,'0.0','2025-04-29 10:45:10','ERR-GK410'),(211,'0.0','2025-04-29 10:45:10','ERR-EDQP3'),(212,'0.0','2025-04-29 10:45:10','ERR-WP663'),(213,'0.0','2025-04-29 10:45:10','ERR-EM05J'),(214,'-1','2025-04-29 10:45:12','ERR-I25DN'),(215,'-1','2025-04-29 10:45:12','ERR-Q81PK'),(216,'0.0','2025-04-29 10:45:15','ERR-95HEX'),(217,'0.0','2025-04-29 10:45:15','ERR-GK410'),(218,'0.0','2025-04-29 10:45:15','ERR-EDQP3'),(219,'0.0','2025-04-29 10:45:15','ERR-WP663'),(220,'0.0','2025-04-29 10:45:15','ERR-EM05J'),(221,'0.0','2025-04-29 10:45:20','ERR-95HEX'),(222,'0.0','2025-04-29 10:45:20','ERR-GK410'),(223,'0.0','2025-04-29 10:45:20','ERR-EDQP3'),(224,'0.0','2025-04-29 10:45:20','ERR-WP663'),(225,'0.0','2025-04-29 10:45:20','ERR-EM05J'),(226,'-1','2025-04-29 10:45:22','ERR-I25DN'),(227,'-1','2025-04-29 10:45:22','ERR-Q81PK'),(228,'0.0','2025-04-29 10:45:26','ERR-95HEX'),(229,'0.0','2025-04-29 10:45:26','ERR-GK410'),(230,'0.0','2025-04-29 10:45:26','ERR-EDQP3'),(231,'0.0','2025-04-29 10:45:26','ERR-WP663'),(232,'0.0','2025-04-29 10:45:26','ERR-EM05J'),(233,'0.0','2025-04-29 10:45:31','ERR-95HEX'),(234,'0.0','2025-04-29 10:45:31','ERR-GK410'),(235,'0.0','2025-04-29 10:45:31','ERR-EDQP3'),(236,'0.0','2025-04-29 10:45:31','ERR-WP663'),(237,'0.0','2025-04-29 10:45:31','ERR-EM05J'),(238,'-1','2025-04-29 10:45:32','ERR-I25DN'),(239,'-1','2025-04-29 10:45:32','ERR-Q81PK'),(240,'0.0','2025-04-29 10:45:36','ERR-95HEX'),(241,'0.0','2025-04-29 10:45:36','ERR-GK410'),(242,'0.0','2025-04-29 10:45:36','ERR-EDQP3'),(243,'0.0','2025-04-29 10:45:36','ERR-WP663'),(244,'0.0','2025-04-29 10:45:36','ERR-EM05J'),(245,'0.0','2025-04-29 10:45:42','ERR-95HEX'),(246,'0.0','2025-04-29 10:45:42','ERR-GK410'),(247,'0.0','2025-04-29 10:45:42','ERR-EDQP3'),(248,'0.0','2025-04-29 10:45:42','ERR-WP663'),(249,'0.0','2025-04-29 10:45:42','ERR-EM05J'),(250,'-1','2025-04-29 10:45:42','ERR-I25DN'),(251,'-1','2025-04-29 10:45:42','ERR-Q81PK'),(252,'0.0','2025-04-29 10:45:47','ERR-95HEX'),(253,'0.0','2025-04-29 10:45:47','ERR-GK410'),(254,'0.0','2025-04-29 10:45:47','ERR-EDQP3'),(255,'0.0','2025-04-29 10:45:47','ERR-WP663'),(256,'0.0','2025-04-29 10:45:47','ERR-EM05J'),(257,'-1','2025-04-29 10:45:52','ERR-I25DN'),(258,'-1','2025-04-29 10:45:52','ERR-Q81PK'),(259,'0.0','2025-04-29 10:45:52','ERR-95HEX'),(260,'0.0','2025-04-29 10:45:52','ERR-GK410'),(261,'0.0','2025-04-29 10:45:52','ERR-EDQP3'),(262,'0.0','2025-04-29 10:45:52','ERR-WP663'),(263,'0.0','2025-04-29 10:45:52','ERR-EM05J'),(264,'0.0','2025-04-29 10:45:58','ERR-95HEX'),(265,'0.0','2025-04-29 10:45:58','ERR-GK410'),(266,'0.0','2025-04-29 10:45:58','ERR-EDQP3'),(267,'0.0','2025-04-29 10:45:58','ERR-WP663'),(268,'0.0','2025-04-29 10:45:58','ERR-EM05J'),(269,'-1','2025-04-29 10:46:02','ERR-I25DN'),(270,'-1','2025-04-29 10:46:02','ERR-Q81PK'),(271,'0.0','2025-04-29 10:46:03','ERR-95HEX'),(272,'0.0','2025-04-29 10:46:03','ERR-GK410'),(273,'0.0','2025-04-29 10:46:03','ERR-EDQP3'),(274,'0.0','2025-04-29 10:46:03','ERR-WP663'),(275,'0.0','2025-04-29 10:46:03','ERR-EM05J'),(276,'0.0','2025-04-29 10:46:08','ERR-95HEX'),(277,'0.0','2025-04-29 10:46:08','ERR-GK410'),(278,'0.0','2025-04-29 10:46:08','ERR-EDQP3'),(279,'0.0','2025-04-29 10:46:08','ERR-WP663'),(280,'0.0','2025-04-29 10:46:08','ERR-EM05J'),(281,'-1','2025-04-29 10:46:12','ERR-I25DN'),(282,'-1','2025-04-29 10:46:12','ERR-Q81PK'),(283,'0.0','2025-04-29 10:46:13','ERR-95HEX'),(284,'0.0','2025-04-29 10:46:13','ERR-GK410'),(285,'0.0','2025-04-29 10:46:13','ERR-EDQP3'),(286,'0.0','2025-04-29 10:46:13','ERR-WP663'),(287,'0.0','2025-04-29 10:46:13','ERR-EM05J'),(288,'0.0','2025-04-29 10:46:19','ERR-95HEX'),(289,'0.0','2025-04-29 10:46:19','ERR-GK410'),(290,'0.0','2025-04-29 10:46:19','ERR-EDQP3'),(291,'0.0','2025-04-29 10:46:19','ERR-WP663'),(292,'0.0','2025-04-29 10:46:19','ERR-EM05J'),(293,'-1','2025-04-29 10:46:22','ERR-I25DN'),(294,'-1','2025-04-29 10:46:22','ERR-Q81PK'),(295,'0.0','2025-04-29 10:46:24','ERR-95HEX'),(296,'0.0','2025-04-29 10:46:24','ERR-GK410'),(297,'0.0','2025-04-29 10:46:24','ERR-EDQP3'),(298,'0.0','2025-04-29 10:46:24','ERR-WP663'),(299,'0.0','2025-04-29 10:46:24','ERR-EM05J'),(300,'0.0','2025-04-29 10:46:29','ERR-95HEX'),(301,'0.0','2025-04-29 10:46:29','ERR-GK410'),(302,'0.0','2025-04-29 10:46:29','ERR-EDQP3'),(303,'0.0','2025-04-29 10:46:29','ERR-WP663'),(304,'0.0','2025-04-29 10:46:29','ERR-EM05J'),(305,'-1','2025-04-29 10:46:33','ERR-I25DN'),(306,'-1','2025-04-29 10:46:33','ERR-Q81PK'),(307,'0.0','2025-04-29 10:46:35','ERR-95HEX'),(308,'0.0','2025-04-29 10:46:35','ERR-GK410'),(309,'0.0','2025-04-29 10:46:35','ERR-EDQP3'),(310,'0.0','2025-04-29 10:46:35','ERR-WP663'),(311,'0.0','2025-04-29 10:46:35','ERR-EM05J'),(312,'0.0','2025-04-29 10:46:40','ERR-95HEX'),(313,'0.0','2025-04-29 10:46:40','ERR-GK410'),(314,'0.0','2025-04-29 10:46:40','ERR-EDQP3'),(315,'0.0','2025-04-29 10:46:40','ERR-WP663'),(316,'0.0','2025-04-29 10:46:40','ERR-EM05J'),(317,'-1','2025-04-29 10:46:43','ERR-I25DN'),(318,'-1','2025-04-29 10:46:43','ERR-Q81PK'),(319,'0.0','2025-04-29 10:46:45','ERR-95HEX'),(320,'0.0','2025-04-29 10:46:45','ERR-GK410'),(321,'0.0','2025-04-29 10:46:45','ERR-EDQP3'),(322,'0.0','2025-04-29 10:46:45','ERR-WP663'),(323,'0.0','2025-04-29 10:46:45','ERR-EM05J'),(324,'0.0','2025-04-29 10:46:51','ERR-95HEX'),(325,'0.0','2025-04-29 10:46:51','ERR-GK410'),(326,'0.0','2025-04-29 10:46:51','ERR-EDQP3'),(327,'0.0','2025-04-29 10:46:51','ERR-WP663'),(328,'0.0','2025-04-29 10:46:51','ERR-EM05J'),(329,'-1','2025-04-29 10:46:53','ERR-I25DN'),(330,'-1','2025-04-29 10:46:53','ERR-Q81PK'),(331,'0.0','2025-04-29 10:46:56','ERR-95HEX'),(332,'0.0','2025-04-29 10:46:56','ERR-GK410'),(333,'0.0','2025-04-29 10:46:56','ERR-EDQP3'),(334,'0.0','2025-04-29 10:46:56','ERR-WP663'),(335,'0.0','2025-04-29 10:46:56','ERR-EM05J'),(336,'0.0','2025-04-29 10:47:01','ERR-95HEX'),(337,'0.0','2025-04-29 10:47:01','ERR-GK410'),(338,'0.0','2025-04-29 10:47:01','ERR-EDQP3'),(339,'0.0','2025-04-29 10:47:01','ERR-WP663'),(340,'0.0','2025-04-29 10:47:01','ERR-EM05J'),(341,'-1','2025-04-29 10:47:03','ERR-I25DN'),(342,'-1','2025-04-29 10:47:03','ERR-Q81PK'),(343,'0.0','2025-04-29 10:47:07','ERR-95HEX'),(344,'0.0','2025-04-29 10:47:07','ERR-GK410'),(345,'0.0','2025-04-29 10:47:07','ERR-EDQP3'),(346,'0.0','2025-04-29 10:47:07','ERR-WP663'),(347,'0.0','2025-04-29 10:47:07','ERR-EM05J'),(348,'0.0','2025-04-29 10:47:12','ERR-95HEX'),(349,'0.0','2025-04-29 10:47:12','ERR-GK410'),(350,'0.0','2025-04-29 10:47:12','ERR-EDQP3'),(351,'0.0','2025-04-29 10:47:12','ERR-WP663'),(352,'0.0','2025-04-29 10:47:12','ERR-EM05J'),(353,'-1','2025-04-29 10:47:13','ERR-I25DN'),(354,'-1','2025-04-29 10:47:13','ERR-Q81PK'),(355,'0.0','2025-04-29 10:47:17','ERR-95HEX'),(356,'0.0','2025-04-29 10:47:17','ERR-GK410'),(357,'0.0','2025-04-29 10:47:17','ERR-EDQP3'),(358,'0.0','2025-04-29 10:47:17','ERR-WP663'),(359,'0.0','2025-04-29 10:47:17','ERR-EM05J'),(360,'0.0','2025-04-29 10:47:23','ERR-95HEX'),(361,'0.0','2025-04-29 10:47:23','ERR-GK410'),(362,'0.0','2025-04-29 10:47:23','ERR-EDQP3'),(363,'0.0','2025-04-29 10:47:23','ERR-WP663'),(364,'0.0','2025-04-29 10:47:23','ERR-EM05J'),(365,'-1','2025-04-29 10:47:23','ERR-I25DN'),(366,'-1','2025-04-29 10:47:23','ERR-Q81PK'),(367,'0.0','2025-04-29 10:47:28','ERR-95HEX'),(368,'0.0','2025-04-29 10:47:28','ERR-GK410'),(369,'0.0','2025-04-29 10:47:28','ERR-EDQP3'),(370,'0.0','2025-04-29 10:47:28','ERR-WP663'),(371,'0.0','2025-04-29 10:47:28','ERR-EM05J'),(372,'-1','2025-04-29 10:47:33','ERR-I25DN'),(373,'-1','2025-04-29 10:47:33','ERR-Q81PK'),(374,'0.0','2025-04-29 10:47:33','ERR-95HEX'),(375,'0.0','2025-04-29 10:47:33','ERR-GK410'),(376,'0.0','2025-04-29 10:47:33','ERR-EDQP3'),(377,'0.0','2025-04-29 10:47:33','ERR-WP663'),(378,'0.0','2025-04-29 10:47:33','ERR-EM05J'),(379,'0.0','2025-04-29 10:47:39','ERR-95HEX'),(380,'0.0','2025-04-29 10:47:39','ERR-GK410'),(381,'0.0','2025-04-29 10:47:39','ERR-EDQP3'),(382,'0.0','2025-04-29 10:47:39','ERR-WP663'),(383,'0.0','2025-04-29 10:47:39','ERR-EM05J'),(384,'-1','2025-04-29 10:47:43','ERR-I25DN'),(385,'-1','2025-04-29 10:47:43','ERR-Q81PK'),(386,'0.0','2025-04-29 10:47:44','ERR-95HEX'),(387,'0.0','2025-04-29 10:47:44','ERR-GK410'),(388,'0.0','2025-04-29 10:47:44','ERR-EDQP3'),(389,'0.0','2025-04-29 10:47:44','ERR-WP663'),(390,'0.0','2025-04-29 10:47:44','ERR-EM05J'),(391,'0.0','2025-04-29 10:47:49','ERR-95HEX'),(392,'0.0','2025-04-29 10:47:49','ERR-GK410'),(393,'0.0','2025-04-29 10:47:49','ERR-EDQP3'),(394,'0.0','2025-04-29 10:47:49','ERR-WP663'),(395,'0.0','2025-04-29 10:47:49','ERR-EM05J'),(396,'-1','2025-04-29 10:47:53','ERR-I25DN'),(397,'-1','2025-04-29 10:47:53','ERR-Q81PK'),(398,'0.0','2025-04-29 10:47:55','ERR-95HEX'),(399,'0.0','2025-04-29 10:47:55','ERR-GK410'),(400,'0.0','2025-04-29 10:47:55','ERR-EDQP3'),(401,'0.0','2025-04-29 10:47:55','ERR-WP663'),(402,'0.0','2025-04-29 10:47:55','ERR-EM05J'),(403,'0.0','2025-04-29 10:48:00','ERR-95HEX'),(404,'0.0','2025-04-29 10:48:00','ERR-GK410'),(405,'0.0','2025-04-29 10:48:00','ERR-EDQP3'),(406,'0.0','2025-04-29 10:48:00','ERR-WP663'),(407,'0.0','2025-04-29 10:48:00','ERR-EM05J'),(408,'-1','2025-04-29 10:48:03','ERR-I25DN'),(409,'-1','2025-04-29 10:48:03','ERR-Q81PK'),(410,'0.0','2025-04-29 10:48:05','ERR-95HEX'),(411,'0.0','2025-04-29 10:48:05','ERR-GK410'),(412,'0.0','2025-04-29 10:48:05','ERR-EDQP3'),(413,'0.0','2025-04-29 10:48:05','ERR-WP663'),(414,'0.0','2025-04-29 10:48:05','ERR-EM05J'),(415,'0.0','2025-04-29 10:48:10','ERR-95HEX'),(416,'0.0','2025-04-29 10:48:10','ERR-GK410'),(417,'0.0','2025-04-29 10:48:10','ERR-EDQP3'),(418,'0.0','2025-04-29 10:48:10','ERR-WP663'),(419,'0.0','2025-04-29 10:48:10','ERR-EM05J'),(420,'-1','2025-04-29 10:48:14','ERR-I25DN'),(421,'-1','2025-04-29 10:48:14','ERR-Q81PK'),(422,'0.0','2025-04-29 10:48:16','ERR-95HEX'),(423,'0.0','2025-04-29 10:48:16','ERR-GK410'),(424,'0.0','2025-04-29 10:48:16','ERR-EDQP3'),(425,'0.0','2025-04-29 10:48:16','ERR-WP663'),(426,'0.0','2025-04-29 10:48:16','ERR-EM05J'),(427,'0.0','2025-04-29 10:48:21','ERR-95HEX'),(428,'0.0','2025-04-29 10:48:21','ERR-GK410'),(429,'0.0','2025-04-29 10:48:21','ERR-EDQP3'),(430,'0.0','2025-04-29 10:48:21','ERR-WP663'),(431,'0.0','2025-04-29 10:48:21','ERR-EM05J'),(432,'-1','2025-04-29 10:48:24','ERR-I25DN'),(433,'-1','2025-04-29 10:48:24','ERR-Q81PK'),(434,'0.0','2025-04-29 10:48:26','ERR-95HEX'),(435,'0.0','2025-04-29 10:48:26','ERR-GK410'),(436,'0.0','2025-04-29 10:48:26','ERR-EDQP3'),(437,'0.0','2025-04-29 10:48:26','ERR-WP663'),(438,'0.0','2025-04-29 10:48:26','ERR-EM05J'),(439,'0.0','2025-04-29 10:48:32','ERR-95HEX'),(440,'0.0','2025-04-29 10:48:32','ERR-GK410'),(441,'0.0','2025-04-29 10:48:32','ERR-EDQP3'),(442,'0.0','2025-04-29 10:48:32','ERR-WP663'),(443,'0.0','2025-04-29 10:48:32','ERR-EM05J'),(444,'-1','2025-04-29 10:48:34','ERR-I25DN'),(445,'-1','2025-04-29 10:48:34','ERR-Q81PK'),(446,'0.0','2025-04-29 10:48:37','ERR-95HEX'),(447,'0.0','2025-04-29 10:48:37','ERR-GK410'),(448,'0.0','2025-04-29 10:48:37','ERR-EDQP3'),(449,'0.0','2025-04-29 10:48:37','ERR-WP663'),(450,'0.0','2025-04-29 10:48:37','ERR-EM05J'),(451,'0.0','2025-04-29 10:48:42','ERR-95HEX'),(452,'0.0','2025-04-29 10:48:42','ERR-GK410'),(453,'0.0','2025-04-29 10:48:42','ERR-EDQP3'),(454,'0.0','2025-04-29 10:48:42','ERR-WP663'),(455,'0.0','2025-04-29 10:48:42','ERR-EM05J'),(456,'-1','2025-04-29 10:48:44','ERR-I25DN'),(457,'-1','2025-04-29 10:48:44','ERR-Q81PK'),(458,'0.0','2025-04-29 10:48:47','ERR-95HEX'),(459,'0.0','2025-04-29 10:48:47','ERR-GK410'),(460,'0.0','2025-04-29 10:48:47','ERR-EDQP3'),(461,'0.0','2025-04-29 10:48:47','ERR-WP663'),(462,'0.0','2025-04-29 10:48:47','ERR-EM05J'),(463,'0.0','2025-04-29 10:48:53','ERR-95HEX'),(464,'0.0','2025-04-29 10:48:53','ERR-GK410'),(465,'0.0','2025-04-29 10:48:53','ERR-EDQP3'),(466,'0.0','2025-04-29 10:48:53','ERR-WP663'),(467,'0.0','2025-04-29 10:48:53','ERR-EM05J'),(468,'-1','2025-04-29 10:48:54','ERR-I25DN'),(469,'-1','2025-04-29 10:48:54','ERR-Q81PK'),(470,'0.0','2025-04-29 10:48:58','ERR-95HEX'),(471,'0.0','2025-04-29 10:48:58','ERR-GK410'),(472,'0.0','2025-04-29 10:48:58','ERR-EDQP3'),(473,'0.0','2025-04-29 10:48:58','ERR-WP663'),(474,'0.0','2025-04-29 10:48:58','ERR-EM05J'),(475,'0.0','2025-04-29 10:49:03','ERR-95HEX'),(476,'0.0','2025-04-29 10:49:03','ERR-GK410'),(477,'0.0','2025-04-29 10:49:03','ERR-EDQP3'),(478,'0.0','2025-04-29 10:49:03','ERR-WP663'),(479,'0.0','2025-04-29 10:49:03','ERR-EM05J'),(480,'-1','2025-04-29 10:49:04','ERR-I25DN'),(481,'-1','2025-04-29 10:49:04','ERR-Q81PK'),(482,'0.0','2025-04-29 10:49:09','ERR-95HEX'),(483,'0.0','2025-04-29 10:49:09','ERR-GK410'),(484,'0.0','2025-04-29 10:49:09','ERR-EDQP3'),(485,'0.0','2025-04-29 10:49:09','ERR-WP663'),(486,'0.0','2025-04-29 10:49:09','ERR-EM05J'),(487,'-1','2025-04-29 10:49:14','ERR-I25DN'),(488,'-1','2025-04-29 10:49:14','ERR-Q81PK'),(489,'0.0','2025-04-29 10:49:14','ERR-95HEX'),(490,'0.0','2025-04-29 10:49:14','ERR-GK410'),(491,'0.0','2025-04-29 10:49:14','ERR-EDQP3'),(492,'0.0','2025-04-29 10:49:14','ERR-WP663'),(493,'0.0','2025-04-29 10:49:14','ERR-EM05J'),(494,'0.0','2025-04-29 10:49:19','ERR-95HEX'),(495,'0.0','2025-04-29 10:49:19','ERR-GK410'),(496,'0.0','2025-04-29 10:49:19','ERR-EDQP3'),(497,'0.0','2025-04-29 10:49:19','ERR-WP663'),(498,'0.0','2025-04-29 10:49:19','ERR-EM05J'),(499,'-1','2025-04-29 10:49:24','ERR-I25DN'),(500,'-1','2025-04-29 10:49:24','ERR-Q81PK'),(501,'0.0','2025-04-29 10:49:25','ERR-95HEX'),(502,'0.0','2025-04-29 10:49:25','ERR-GK410'),(503,'0.0','2025-04-29 10:49:25','ERR-EDQP3'),(504,'0.0','2025-04-29 10:49:25','ERR-WP663'),(505,'0.0','2025-04-29 10:49:25','ERR-EM05J'),(506,'0.0','2025-04-29 10:49:30','ERR-95HEX'),(507,'0.0','2025-04-29 10:49:30','ERR-GK410'),(508,'0.0','2025-04-29 10:49:30','ERR-EDQP3'),(509,'0.0','2025-04-29 10:49:30','ERR-WP663'),(510,'0.0','2025-04-29 10:49:30','ERR-EM05J'),(511,'-1','2025-04-29 10:49:34','ERR-I25DN'),(512,'-1','2025-04-29 10:49:34','ERR-Q81PK'),(513,'0.0','2025-04-29 10:49:35','ERR-95HEX'),(514,'0.0','2025-04-29 10:49:35','ERR-GK410'),(515,'0.0','2025-04-29 10:49:35','ERR-EDQP3'),(516,'0.0','2025-04-29 10:49:35','ERR-WP663'),(517,'0.0','2025-04-29 10:49:35','ERR-EM05J');
/*!40000 ALTER TABLE `logToleranceAlarmDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `powerDeviceDB`
--

DROP TABLE IF EXISTS `powerDeviceDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `powerDeviceDB` (
  `id` varchar(50) NOT NULL,
  `number` int(11) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `ip` varchar(20) DEFAULT NULL,
  `connection` tinyint(4) DEFAULT NULL,
  `state` tinyint(4) DEFAULT NULL,
  `createdAt` datetime DEFAULT NULL,
  `updatedAt` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `number` (`number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `powerDeviceDB`
--

LOCK TABLES `powerDeviceDB` WRITE;
/*!40000 ALTER TABLE `powerDeviceDB` DISABLE KEYS */;
/*!40000 ALTER TABLE `powerDeviceDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `powerMasterParameterDB`
--

DROP TABLE IF EXISTS `powerMasterParameterDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `powerMasterParameterDB` (
  `id` varchar(50) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `parameterCode` varchar(255) DEFAULT NULL,
  `createdAt` datetime NOT NULL DEFAULT current_timestamp(),
  `updatedAt` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `powerMasterParameterDB`
--

LOCK TABLES `powerMasterParameterDB` WRITE;
/*!40000 ALTER TABLE `powerMasterParameterDB` DISABLE KEYS */;
/*!40000 ALTER TABLE `powerMasterParameterDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `powerMasterSensorDB`
--

DROP TABLE IF EXISTS `powerMasterSensorDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `powerMasterSensorDB` (
  `id` varchar(50) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `sensorId` varchar(255) DEFAULT NULL,
  `createdAt` datetime DEFAULT current_timestamp(),
  `updatedAt` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `powerMasterSensorDB`
--

LOCK TABLES `powerMasterSensorDB` WRITE;
/*!40000 ALTER TABLE `powerMasterSensorDB` DISABLE KEYS */;
/*!40000 ALTER TABLE `powerMasterSensorDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sensorGroupDB`
--

DROP TABLE IF EXISTS `sensorGroupDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sensorGroupDB` (
  `id` varchar(50) NOT NULL,
  `number` varchar(50) DEFAULT NULL,
  `oid` varchar(50) DEFAULT NULL,
  `name` varchar(50) NOT NULL,
  `intervals` int(11) NOT NULL,
  `unit` tinyint(1) NOT NULL,
  `frekuensi` int(11) NOT NULL,
  `service_id` int(11) NOT NULL,
  `enterAlarm` int(11) DEFAULT 1,
  `exitAlarm` int(11) DEFAULT 1,
  `errorAlarm` int(11) DEFAULT 300,
  `state` varchar(2) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sensorGroupDB`
--

LOCK TABLES `sensorGroupDB` WRITE;
/*!40000 ALTER TABLE `sensorGroupDB` DISABLE KEYS */;
INSERT INTO `sensorGroupDB` VALUES ('PGS-44539','6','6','Power Extension',10,1,1,17,600,600,600,'0'),('PGS-5FB52','5','5','Power',1,1,1,12,5,5,600,'0'),('PGS-8C566','8','8','Network',10,1,1,18,600,600,600,'0'),('PGS-A9C7E','4','4','Environment',5,1,1,50,5,5,600,'0'),('PGS-D768E','3','3','Internal',10,1,1,19,1,1,300,'1'),('PGS-DED30','2','2','Environment Extension',10,1,1,16,1,1,300,'1'),('PGS-F99B9','7','7','Remote IR Extension',10,1,1,20,600,600,600,'0'),('PGS-PMT72','1','1','Room',5,1,1,35,1,1,300,'1');
/*!40000 ALTER TABLE `sensorGroupDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sensorListDB`
--

DROP TABLE IF EXISTS `sensorListDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sensorListDB` (
  `id` varchar(50) NOT NULL,
  `sensor_id` varchar(30) NOT NULL,
  `group_id` varchar(50) DEFAULT NULL,
  `oid` bigint(20) DEFAULT NULL,
  `name` varchar(35) NOT NULL,
  `value` varchar(200) DEFAULT NULL,
  `timestamp` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `calibrate` tinyint(1) DEFAULT NULL,
  `formula` bigint(20) DEFAULT NULL,
  `alarm` tinyint(1) DEFAULT 0,
  `max` varchar(30) DEFAULT '0',
  `min` varchar(30) DEFAULT '0',
  `unit` varchar(30) DEFAULT '#',
  `oid_tipe` tinyint(1) DEFAULT NULL,
  `monitor` int(11) DEFAULT 0,
  `log` int(11) DEFAULT 0,
  `alarm_type` int(11) DEFAULT 0,
  `last_sync` datetime DEFAULT NULL,
  `conditions` varchar(50) DEFAULT 'Alarm Inactive',
  `notif_state` int(11) DEFAULT 0,
  `notif_count` int(11) DEFAULT 0,
  `notif_time` int(11) NOT NULL DEFAULT 0,
  `alarmId1` varchar(10) DEFAULT '',
  `alarmId2` varchar(10) DEFAULT '',
  `state` varchar(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `fk_sensorList_group` (`group_id`),
  CONSTRAINT `fk_sensorList_group` FOREIGN KEY (`group_id`) REFERENCES `sensorGroupDB` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sensorListDB`
--

LOCK TABLES `sensorListDB` WRITE;
/*!40000 ALTER TABLE `sensorListDB` DISABLE KEYS */;
INSERT INTO `sensorListDB` VALUES ('PLS-03A2F','humid_p5','PGS-A9C7E',18,'Humidity Port 5','0.0','2025-03-12 14:36:53',0,0,0,'0','0','#',1,0,0,0,NULL,'Alarm Inactive',0,0,0,'','','0'),('PLS-04EED','router1Iface1Latency','PGS-8C566',21,'Router 1 Interface 1 Latency','0.34','2025-04-27 22:51:41',0,0,0,'0','0','ms',0,1,1,0,'2025-04-27 22:51:40','Alarm Inactive',0,0,0,'','','1'),('PLS-09257','router1HddTotal','PGS-8C566',10,'Router 1 HDD Total','131072','2025-04-27 22:51:40',0,0,0,'0','0','KiB',0,1,1,0,'2025-04-27 22:51:40','Alarm Inactive',0,0,0,'','','1'),('PLS-0F2F8','stateAc2','PGS-F99B9',2,'State Remote AC 2','-1','2025-03-12 14:54:55',0,0,0,'1','0','#',0,1,1,-1,'2025-01-23 13:45:31','Alarm Inactive',0,0,0,'','','1'),('PLS-11BUR','smokeP2Ext1','PGS-DED30',2,'Smoke Detector Port 2 Extension 1','-1','2025-06-02 00:31:50',0,0,1,'0','0','#',0,1,1,2,'2025-04-29 10:29:44','Alarm Error',2,4670,10549,'ERR-Q81PK','ERR-Q81PK','1'),('PLS-135D3','smoke_p6','PGS-A9C7E',23,'Smoke Detector Port 6','1','2025-01-07 11:56:18',0,0,0,'0','0','#',1,0,0,0,NULL,'Alarm Inactive',0,0,0,'','','0'),('PLS-1394C','door_p1','PGS-A9C7E',4,'Door State Port 1','1','2025-01-07 11:56:18',0,0,0,'0','0','#',1,0,0,0,NULL,'Alarm Inactive',0,0,0,'','','0'),('PLS-13956','router1Iface1Name','PGS-8C566',17,'Router 1 Interface 1 Name','ether1','2025-04-27 22:51:41',0,0,0,'0','0','#',1,1,1,0,'2025-04-27 22:51:40','Alarm Inactive',0,0,0,'','','1'),('PLS-1874A','router1Volt','PGS-8C566',2,'Router 1 Voltage','0','2025-04-27 22:51:33',0,0,0,'1','0','V',0,0,0,-1,'2025-01-23 13:45:31','Alarm Inactive',0,0,0,'','','1'),('PLS-1D808','router1Iface1DownSpd','PGS-8C566',20,'Router 1 Interface Download Speed','5.57','2025-04-27 22:51:41',0,0,0,'0','0','Mbps',0,1,1,0,'2025-04-27 22:51:40','Alarm Inactive',0,0,0,'','','1'),('PLS-1F995','humid_p4','PGS-A9C7E',14,'Humidity Port 4','0.0','2025-03-12 14:36:53',0,0,0,'0','0','#',1,0,0,0,NULL,'Alarm Inactive',0,0,0,'','','0'),('PLS-233FD','router1Iface1Mac','PGS-8C566',18,'Router 1 Interface Mac Address','48-A9-8A-9B-16-74','2025-04-27 22:51:40',0,0,0,'0','0','#',1,1,1,0,'2025-04-27 22:51:40','Alarm Inactive',0,0,0,'','','1'),('PLS-2B119','router1Model','PGS-8C566',14,'Router 1 Model','RouterOS C53UiG+5HPaxD2HPaxD','2025-04-27 22:51:41',0,0,0,'0','0','#',1,1,1,0,'2025-04-27 22:51:40','Alarm Inactive',0,0,0,'','','1'),('PLS-36F7D','router1MemSpace','PGS-8C566',11,'Router 1 Memory Space','660588','2025-04-27 22:51:40',0,0,0,'0','0','KiB',0,1,1,0,'2025-04-27 22:51:40','Alarm Inactive',0,0,0,'','','1'),('PLS-38801','router1Uptime','PGS-8C566',16,'Router 1 Uptime','13 days, 12:45:55','2025-04-27 22:51:41',0,0,0,'0','0','#',1,1,1,0,'2025-04-27 22:51:40','Alarm Inactive',0,0,0,'','','1'),('PLS-3A1F0','nearonCpuUsage','PGS-D768E',5,'Nearon CPU Usage','16.4','2025-06-02 01:06:01',0,0,0,'0','0','%',0,1,1,0,'2025-04-29 10:29:44','Alarm Inactive',0,0,0,'','','1'),('PLS-3B807','acCurrent3','PGS-5FB52',4,'AC Current Port 3','37.41','2025-04-27 22:51:40',0,0,0,'0','0','A',0,1,1,0,'2025-04-27 22:51:40','Alarm Inactive',0,0,0,'','','1'),('PLS-4155F','router1HddSpace','PGS-8C566',8,'Router 1 HDD Space','93072','2025-04-27 22:51:40',0,0,0,'0','0','KiB',0,1,1,0,'2025-04-27 22:51:40','Alarm Inactive',0,0,0,'','','1'),('PLS-41D1B','temp_p1','PGS-A9C7E',1,'Termperature Port 1','0.0','2025-04-27 22:51:43',0,0,0,'0','0','#',1,0,1,0,NULL,'Alarm Inactive',0,0,0,'','','1'),('PLS-42857','door_p5','PGS-A9C7E',20,'Door State Port 5','1','2025-01-07 11:56:18',0,0,0,'0','0','#',1,0,0,0,NULL,'Alarm Inactive',0,0,0,'','','0'),('PLS-50061','humid_p3','PGS-A9C7E',10,'Humidity Port 3','0.0','2025-01-07 11:56:18',0,0,0,'0','0','#',1,0,0,0,NULL,'Alarm Inactive',0,0,0,'','','0'),('PLS-5C2BC','temp_p5','PGS-A9C7E',17,'Temperature Port 5','0.0','2025-03-12 14:36:53',0,0,0,'0','0','#',1,0,0,0,NULL,'Alarm Inactive',0,0,0,'','','0'),('PLS-5D79E','router1CpuFreq','PGS-8C566',7,'Router 1 CPU Frequency','1320','2025-04-27 22:51:40',0,0,0,'0','0','MHz',0,1,1,0,'2025-04-27 22:51:40','Alarm Inactive',0,0,0,'','','1'),('PLS-5EA4C','humid_p1','PGS-A9C7E',2,'Humidity Port 1','0.0','2025-04-27 22:51:43',0,0,0,'0','0','#',1,0,1,1,NULL,'Alarm Inactive',0,0,0,'','','1'),('PLS-5FDEF','router1CpuLoad4','PGS-8C566',6,'Router 1 CPU Load 4','3','2025-04-27 22:51:40',0,0,0,'0','0','%',0,1,1,0,'2025-04-27 22:51:40','Alarm Inactive',0,0,0,'','','1'),('PLS-6160D','door_p4','PGS-A9C7E',16,'Door State Port 4','1','2025-01-07 11:56:18',0,0,0,'0','0','#',1,0,0,0,NULL,'Alarm Inactive',0,0,0,'','','0'),('PLS-61805','acVoltage','PGS-5FB52',1,'AC Voltage','1.0','2025-04-27 22:51:40',0,0,0,'0','0','V',0,1,1,0,'2025-04-27 22:51:40','Alarm Inactive',0,0,0,'','','1'),('PLS-6FC21','nearonCpuTemp','PGS-D768E',6,'Nearon CPU Temperature','44.8','2025-06-02 01:06:01',0,0,0,'0','0','°C',0,1,1,0,'2025-04-29 10:29:44','Alarm Inactive',0,0,0,'','','1'),('PLS-70F0E','stateAc3','PGS-F99B9',3,'State Remote AC 3','-1','2025-03-12 14:54:55',0,0,0,'1','0','#',0,1,1,-1,'2025-01-23 13:45:31','Alarm Inactive',0,0,0,'','','1'),('PLS-75A3C','acCurrent4','PGS-5FB52',5,'AC Current Port 4','37.41','2025-04-27 22:51:40',0,0,0,'0','0','A',0,1,1,0,'2025-04-27 22:51:40','Alarm Inactive',0,0,0,'','','1'),('PLS-79999','router1SN','PGS-8C566',15,'Router 1 Serial Number','HEA08TJAYNM','2025-04-27 22:51:41',0,0,0,'0','0','#',1,1,1,0,'2025-04-27 22:51:40','Alarm Inactive',0,0,0,'','','1'),('PLS-7B2B3','temp_p4','PGS-A9C7E',13,'Temperature Port 4','0.0','2025-03-12 14:36:53',0,0,0,'0','0','#',1,0,0,0,NULL,'Alarm Inactive',0,0,0,'','','0'),('PLS-7C21C','router1MemTotal','PGS-8C566',13,'Router 1 Memory Total','1048576','2025-04-27 22:51:41',0,0,0,'0','0','KiB',0,1,1,0,'2025-04-27 22:51:40','Alarm Inactive',0,0,0,'','','1'),('PLS-7JIGS','pm1','PGS-PMT72',1,'PM1','0.0','2025-06-02 00:31:50',0,0,0,'0','0','µg/m3',0,1,1,0,'2025-04-29 10:29:44','Alarm Inactive',0,0,0,'','','1'),('PLS-80F6A','smoke_p4','PGS-A9C7E',15,'Smoke Detector Port 4','1','2025-01-07 11:56:18',0,0,0,'0','0','#',1,0,0,0,NULL,'Alarm Inactive',0,0,0,'','','0'),('PLS-82E43','temp_p3','PGS-A9C7E',9,'Temperature Port 3','0.0','2025-01-07 11:56:18',0,0,0,'0','0','#',1,0,0,0,NULL,'Alarm Inactive',0,0,0,'','','0'),('PLS-86B1C','nearonMemUsage','PGS-D768E',7,'Nearon Memory Usage','16','2025-06-02 01:06:01',0,0,0,'0','0','%',0,1,1,0,'2025-04-29 10:29:44','Alarm Inactive',0,0,0,'','','1'),('PLS-877A1','smoke_p1','PGS-A9C7E',3,'Smoke Detector Port 1','1','2025-01-07 11:56:18',0,0,0,'0','0','#',1,0,0,0,NULL,'Alarm Inactive',0,0,0,'','','0'),('PLS-8DC72','temp_p6','PGS-A9C7E',21,'Temperature Port 6',NULL,'2025-01-07 11:56:18',0,0,0,'0','0','#',1,0,0,0,NULL,'Alarm Inactive',0,0,0,'','','0'),('PLS-9C17D','nearonStorageUsage','PGS-D768E',8,'Nearon Storage Usage','14','2025-06-02 01:06:01',0,0,0,'0','0','%',0,1,1,0,'2025-04-29 10:29:44','Alarm Inactive',0,0,0,'','','1'),('PLS-9D726','router1CpuLoad3','PGS-8C566',5,'Router 1 CPU Load 3','2','2025-04-27 22:51:40',0,0,0,'0','0','%',0,1,1,0,'2025-04-27 22:51:40','Alarm Inactive',0,0,0,'','','1'),('PLS-9E5B7','router1CpuLoad2','PGS-8C566',4,'Router 1 CPU Load 2','2','2025-04-27 22:51:40',0,0,0,'0','0','%',0,1,1,0,'2025-04-27 22:51:40','Alarm Inactive',0,0,0,'','','1'),('PLS-9F3AF','smoke_p5','PGS-A9C7E',19,'Smoke Detector Port 5','1','2025-04-27 22:51:43',0,0,0,'0','0','#',1,0,1,0,NULL,'Alarm Inactive',0,0,0,'','','1'),('PLS-A37DD','humid_p2','PGS-A9C7E',6,'Humidity Port 2',NULL,'2025-01-07 11:56:18',0,0,0,'0','0','#',1,0,0,0,NULL,'Alarm Inactive',0,0,0,'','','0'),('PLS-A6AA0','temp_p2','PGS-A9C7E',5,'Temperature Port 2',NULL,'2025-01-07 11:56:18',0,0,0,'0','0','#',1,0,0,0,NULL,'Alarm Inactive',0,0,0,'','','0'),('PLS-A787E','router1HddUsed','PGS-8C566',9,'Router 1 HDD Used','38000','2025-04-27 22:51:40',0,0,0,'0','0','KiB',0,1,1,0,'2025-04-27 22:51:40','Alarm Inactive',0,0,0,'','','1'),('PLS-AD534','router1MemUsed','PGS-8C566',12,'Router 1 Memory Used	','387988','2025-04-27 22:51:41',0,0,0,'0','0','KiB',0,1,1,0,'2025-04-27 22:51:40','Alarm Inactive',0,0,0,'','','1'),('PLS-B1D00','nearonVolt','PGS-D768E',1,'Nearon Input Voltage','0.01','2025-06-02 00:31:51',0,0,0,'-4','-1','#',0,0,0,0,NULL,'Alarm Inactive',0,0,0,'','','1'),('PLS-C8FB2','nearonFan','PGS-D768E',4,'Nearon Fan Speed','100','2025-06-02 01:06:01',0,0,0,'-4','-1','#',0,0,0,3,NULL,'Alarm Inactive',0,0,0,'','','1'),('PLS-CE8CD','stateAc4','PGS-F99B9',4,'State Remote AC 4','-1','2025-01-23 13:45:31',0,0,0,'1','0','#',0,1,0,-1,'2025-01-23 13:45:31','Alarm Inactive',0,0,0,'','','0'),('PLS-CF50D','stateAc1','PGS-F99B9',1,'State Remote AC 1','-1','2025-03-12 14:54:55',0,0,0,'1','0','#',0,1,1,-1,'2025-01-23 13:45:31','Alarm Inactive',0,0,0,'','','1'),('PLS-D264E','router1Iface1UpSpd','PGS-8C566',19,'Router 1 Interface 1 Upload Speed','0.26','2025-04-27 22:51:41',0,0,0,'0','0','Mbps',0,1,1,0,'2025-04-27 22:51:40','Alarm Inactive',0,0,0,'','','1'),('PLS-D39F9','acCurrent2','PGS-5FB52',3,'AC Current Port 2','37.41','2025-04-27 22:51:40',0,0,0,'0','0','A',0,1,1,0,'2025-04-27 22:51:40','Alarm Inactive',0,0,0,'','','1'),('PLS-D9BBC','smoke_p2','PGS-A9C7E',7,'Smoke Detector Port 2','1','2025-03-12 14:36:53',0,0,0,'0','0','#',1,0,0,0,NULL,'Alarm Inactive',0,0,0,'','','0'),('PLS-DF157','router1CpuLoad1','PGS-8C566',3,'Router 1 CPU Load 1','4','2025-04-27 22:51:40',0,0,0,'0','0','%',0,1,1,0,'2025-04-27 22:51:40','Alarm Inactive',0,0,0,'','','1'),('PLS-DRG90','temp','PGS-PMT72',4,'Temperature','0.0','2025-06-02 00:31:50',0,0,1,'25','18','°C',0,1,1,3,'2025-04-29 10:29:44','Alarm Error',2,8457,10556,'ERR-EDQP3','ERR-EDQP3','1'),('PLS-E29BD','humid_p6','PGS-A9C7E',22,'Humidity Port 6',NULL,'2025-01-07 11:56:18',0,0,0,'0','0','#',1,0,0,0,NULL,'Alarm Inactive',0,0,0,'','','0'),('PLS-E3DB7','door_p6','PGS-A9C7E',24,'Door State Port 6','1','2025-01-07 11:56:18',0,0,0,'0','0','#',1,0,0,0,NULL,'Alarm Inactive',0,0,0,'','','0'),('PLS-E7327','door_p3','PGS-A9C7E',12,'Door State Port 3','1','2025-04-27 22:51:43',0,0,0,'0','0','#',1,0,1,0,NULL,'Alarm Inactive',0,0,0,'','','1'),('PLS-EA12A','pm10','PGS-PMT72',3,'PM10','0.0','2025-06-02 00:31:50',0,0,1,'50','0','µg/m3',0,1,1,2,'2025-04-29 10:29:44','Alarm Error',2,8457,10556,'ERR-GK410','ERR-GK410','1'),('PLS-EF3ED','door_p2','PGS-A9C7E',8,'Door State Port 2','1','2025-01-07 11:56:18',0,0,0,'0','0','#',1,0,0,0,NULL,'Alarm Inactive',0,0,0,'','','0'),('PLS-EKWYS','pm25','PGS-PMT72',2,'PM2.5','0.0','2025-06-02 00:31:50',0,0,1,'35','0','µg/m3',0,1,1,2,'2025-04-29 10:29:44','Alarm Error',2,8457,10556,'ERR-95HEX','ERR-95HEX','1'),('PLS-F1A63','router1Temp','PGS-8C566',1,'Router 1 Temperature','0','2025-04-27 22:51:33',0,0,0,'1','0','°C',0,0,0,-1,'2025-01-23 13:45:31','Alarm Inactive',0,0,0,'','','1'),('PLS-F2294','acCurrent1','PGS-5FB52',2,'AC Current Port 1','37.41','2025-04-27 22:51:40',0,0,0,'0','0','A',0,1,1,0,'2025-04-27 22:51:40','Alarm Inactive',0,0,0,'','','1'),('PLS-F7599','smoke_p3','PGS-A9C7E',11,'Smoke Detector Port 3','1','2025-01-07 11:56:18',0,0,0,'0','0','#',1,0,0,0,NULL,'Alarm Inactive',0,0,0,'','','0'),('PLS-FD654','nearonUptime','PGS-D768E',9,'Nearon Uptime','8 hours  03 minutes  01 second','2025-06-02 01:06:01',0,0,0,'0','0','#',1,1,1,0,'2025-04-29 10:29:44','Alarm Inactive',0,0,0,'','','1'),('PLS-FF4CD','nearonLastBoot','PGS-D768E',10,'Nearon Last Boot','2025-06-01 17:03:00','2025-06-02 01:06:01',0,0,0,'0','0','#',1,1,1,0,'2025-04-29 10:29:44','Alarm Inactive',0,0,0,'','','1'),('PLS-FUJUG','co2','PGS-PMT72',6,'CO2','0.0','2025-06-02 00:31:50',0,0,1,'1000','350','ppm',0,1,1,3,'2025-04-29 10:29:44','Alarm Error',2,8457,10557,'ERR-EM05J','ERR-EM05J','1'),('PLS-IPF33','humid','PGS-PMT72',5,'Humidity','0.0','2025-06-02 00:31:50',0,0,1,'60','40','%',0,1,1,3,'2025-04-29 10:29:44','Alarm Error',2,8457,10556,'ERR-WP663','ERR-WP663','1'),('PLS-KWRPX','nox','PGS-PMT72',8,'NOx','0.0','2025-06-02 00:31:50',0,0,0,'0','0','#',0,1,1,0,'2025-04-29 10:29:44','Alarm Inactive',0,0,0,'','','1'),('PLS-LSB04','voc','PGS-PMT72',7,'VOC','0.0','2025-06-02 00:31:50',0,0,0,'0','0','#',0,1,1,0,'2025-04-29 10:29:44','Alarm Inactive',0,0,0,'','','1'),('PLS-UOSFI','smokeP1Ext1','PGS-DED30',1,'Smoke Detector Port 1 Extension 1','-1','2025-06-02 00:31:50',0,0,1,'0','0','#',0,1,1,2,'2025-04-29 10:29:44','Alarm Error',2,4670,10549,'ERR-I25DN','ERR-I25DN','1');
/*!40000 ALTER TABLE `sensorListDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sensorParameterGroupDB`
--

DROP TABLE IF EXISTS `sensorParameterGroupDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sensorParameterGroupDB` (
  `id` varchar(50) NOT NULL,
  `group_id` varchar(50) DEFAULT NULL,
  `name` varchar(100) NOT NULL,
  `parameter` varchar(100) NOT NULL,
  `value` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_sensorParamGroup_group` (`group_id`),
  CONSTRAINT `fk_sensorParamGroup_group` FOREIGN KEY (`group_id`) REFERENCES `sensorGroupDB` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sensorParameterGroupDB`
--

LOCK TABLES `sensorParameterGroupDB` WRITE;
/*!40000 ALTER TABLE `sensorParameterGroupDB` DISABLE KEYS */;
INSERT INTO `sensorParameterGroupDB` VALUES ('PPG-152D2','PGS-8C566','OID Router Memory Used','oidRouterMemUsed','1.3.6.1.2.1.25.2.3.1.6.65536'),('PPG-16ED3','PGS-5FB52','Port AC Current 3 Status','portCurrent3','on'),('PPG-1B460','PGS-DED30','Endpoint','endpoint','/api/get/sensor/data'),('PPG-1DA9B','PGS-F99B9','Endpoint','endpoint','/api/set/remote/ac'),('PPG-1FE8F','PGS-DED30','Parent OID','parent_oid','1.3.6.1.4.1.19719.2'),('PPG-2C174','PGS-A9C7E','Port Door 2 Status','portDoor2','on'),('PPG-33538','PGS-8C566','OID Router Temperature','oidRouterTemp','1.3.6.1.4.1.14988.1.1.3.10.0'),('PPG-3A283','PGS-F99B9','Parent OID','parent_oid','1.3.6.1.4.1.19719.7'),('PPG-3AA5E','PGS-A9C7E','Port Smoke 2 Status','portSmoke2','on'),('PPG-3EA9B','PGS-A9C7E','Power Cut Off','power_cut_off','1'),('PPG-475FC','PGS-DED30','Modbus Port','modbus_port','/dev/ttyUSB0'),('PPG-5B360','PGS-5FB52','Port AC Current 4 Status','portCurrent4','on'),('PPG-6EA39','PGS-5FB52','Parent OID','parent_oid','1.3.6.1.4.1.19719.5'),('PPG-6F64D','PGS-8C566','Community Router 1','comRouter1','public'),('PPG-738DD','PGS-A9C7E','Port Door 1 Status','portDoor1','on'),('PPG-75579','PGS-8C566','OID Router Uptime','oidRouterUptime','1.3.6.1.2.1.1.3.0'),('PPG-7624F','PGS-5FB52','Port AC Current 1 Status','portCurrent1','on'),('PPG-78B02','PGS-A9C7E','Modbus ID Temperature 2','modbusId2','2'),('PPG-79091','PGS-A9C7E','Modbus ID Temperature 1','modbusId1','1'),('PPG-7C760','PGS-44539','Device Extension Status 1','deviceExt1','on'),('PPG-83323','PGS-A9C7E','Port Temperature 1 Status','portTemp1','on'),('PPG-89271','PGS-D768E','Parent OID','parent_oid','1.3.6.1.4.1.19719.3'),('PPG-895BC','PGS-8C566','OID Router Voltage','oidRouterVolt','1.3.6.1.4.1.14988.1.1.3.8.0'),('PPG-8ERTY','PGS-PMT72','Parent OID','parent_oid','1.3.6.1.4.1.19719.1'),('PPG-90ED0','PGS-44539','Endpoint','endpoint','/api/get/sensor/data'),('PPG-A0A95','PGS-8C566','OID Router HDD Total ','oidRouterHddTotal','1.3.6.1.2.1.25.2.3.1.5.131072'),('PPG-AA13F','PGS-8C566','Port SNMP Router 1','portRouter1','161'),('PPG-AD9FB','PGS-8C566','OID Router Model','oidRouterModel','1.3.6.1.2.1.1.1.0'),('PPG-AFEDA','PGS-8C566','IP Address Router 1','ipRouter1','10.19.50.1'),('PPG-B4214','PGS-A9C7E','Parent OID','parent_oid','1.3.6.1.4.1.19719.4'),('PPG-B4727','PGS-8C566','OID Router CPU Frequency','oidRouterCpuFreq','1.3.6.1.4.1.14988.1.1.3.14.0'),('PPG-B66D3','PGS-8C566','Parent OID','parent_oid','1.3.6.1.4.1.19719.8'),('PPG-BDCFC','PGS-A9C7E','Port Serial','portSerial','/dev/ttyS0'),('PPG-C72E0','PGS-5FB52','Sensitivity AC Current','sensitivityCurrent','0.066'),('PPG-CE231','PGS-8C566','OID Router HDD Used ','oidRouterHddUsed','1.3.6.1.2.1.25.2.3.1.6.131072'),('PPG-D45C5','PGS-5FB52','Sensitivity AC Voltage','sensitivityVoltage','631'),('PPG-D62F2','PGS-8C566','OID Router Serial Number','oidRouterSN','1.3.6.1.4.1.14988.1.1.7.3.0'),('PPG-DCC77','PGS-F99B9','Device Extension Status','deviceExt','on'),('PPG-DDFCB','PGS-5FB52','Port AC Current 2 Status','portCurrent2','on'),('PPG-DED0B','PGS-A9C7E','Port Temperature 2 Status ','portTemp2','on'),('PPG-E8DE1','PGS-A9C7E','Port Smoke 1 Status','portSmoke1','on'),('PPG-F94CB','PGS-44539','Parent OID','parent_oid','1.3.6.1.4.1.19719.6'),('PPG-F9QZW','PGS-PMT72','IP Address','ip','10.19.53.71'),('PPG-FCDA8','PGS-8C566','OID Router Memory Total','oidRouterMemTotal','1.3.6.1.2.1.25.2.3.1.5.65536'),('PPG-FD513','PGS-F99B9','IP Address Device Extension','ipExt','10.19.54.11');
/*!40000 ALTER TABLE `sensorParameterGroupDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sensorParameterListDB`
--

DROP TABLE IF EXISTS `sensorParameterListDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sensorParameterListDB` (
  `id` varchar(50) NOT NULL,
  `sensor_id` varchar(50) DEFAULT NULL,
  `name` varchar(100) NOT NULL,
  `parameter` varchar(100) NOT NULL,
  `value` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_sensorParameterList_sensor_id` (`sensor_id`),
  CONSTRAINT `fk_sensorParameterList_sensor_id` FOREIGN KEY (`sensor_id`) REFERENCES `sensorListDB` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sensorParameterListDB`
--

LOCK TABLES `sensorParameterListDB` WRITE;
/*!40000 ALTER TABLE `sensorParameterListDB` DISABLE KEYS */;
INSERT INTO `sensorParameterListDB` VALUES ('PPL-0E36E','PLS-75A3C','Pin','pin','3'),('PPL-10ED9','PLS-B1D00','Pin','pin','0'),('PPL-2B870','PLS-9D726','OID','oid','1.3.6.1.2.1.25.3.3.1.2.3'),('PPL-59DFC','PLS-04EED','Timeout Ping','timeout','1'),('PPL-7EA49','PLS-1D808','OID','oid','1.3.6.1.4.1.14988.1.1.14.1.1.31.1'),('PPL-8556B','PLS-5FDEF','OID','oid','1.3.6.1.2.1.25.3.3.1.2.4'),('PPL-8AE6D','PLS-233FD','OID','oid','1.3.6.1.2.1.2.2.1.6.1'),('PPL-9D02E','PLS-D39F9','Pin','pin','7'),('PPL-ACEA2','PLS-9E5B7','OID','oid','1.3.6.1.2.1.25.3.3.1.2.2'),('PPL-B4A27','PLS-13956','OID','oid','1.3.6.1.4.1.14988.1.1.14.1.1.2.1'),('PPL-B8866','PLS-04EED','Size Packet','sizePacket','32'),('PPL-C2A83','PLS-D264E','OID','oid','1.3.6.1.4.1.14988.1.1.14.1.1.61.1'),('PPL-CD8C2','PLS-3B807','Pin','pin','5'),('PPL-D2923','PLS-04EED','Count Packet','countPacket','4'),('PPL-DA189','PLS-B1D00','Offset','offset','5.3'),('PPL-E6812','PLS-61805','Pin','pin','6'),('PPL-E8A7C','PLS-DF157','OID','oid','1.3.6.1.2.1.25.3.3.1.2.1'),('PPL-ED259','PLS-F2294','Pin','pin','1');
/*!40000 ALTER TABLE `sensorParameterListDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sensorPortConfigDB`
--

DROP TABLE IF EXISTS `sensorPortConfigDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sensorPortConfigDB` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `type` varchar(10) DEFAULT NULL,
  `modbus_id` varchar(100) DEFAULT NULL,
  `digital_pin` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sensorPortConfigDB`
--

LOCK TABLES `sensorPortConfigDB` WRITE;
/*!40000 ALTER TABLE `sensorPortConfigDB` DISABLE KEYS */;
INSERT INTO `sensorPortConfigDB` VALUES (1,'port_1','1','1','32'),(2,'port_2','0','2','33'),(3,'port_3','3','3','21'),(4,'port_4','0','4','22'),(5,'port_5','2','5','12'),(6,'port_6','0','6','24');
/*!40000 ALTER TABLE `sensorPortConfigDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `serverHttpAuthDB`
--

DROP TABLE IF EXISTS `serverHttpAuthDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `serverHttpAuthDB` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `value` varchar(10000) NOT NULL,
  `updatedAt` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `serverHttpAuthDB`
--

LOCK TABLES `serverHttpAuthDB` WRITE;
/*!40000 ALTER TABLE `serverHttpAuthDB` DISABLE KEYS */;
INSERT INTO `serverHttpAuthDB` VALUES (1,'token','eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlX2lkIjoiMSIsInBlcm1pc3Npb25zIjp7IjEiOnRydWUsIjEwIjp0cnVlLCIxMSI6dHJ1ZSwiMTIiOnRydWUsIjEzIjp0cnVlLCIxNCI6dHJ1ZSwiMTUiOnRydWUsIjE2Ijp0cnVlLCIxNyI6dHJ1ZSwiMTgiOnRydWUsIjE5Ijp0cnVlLCIyIjp0cnVlLCIyMCI6dHJ1ZSwiMjEiOnRydWUsIjIyIjp0cnVlLCIyMyI6dHJ1ZSwiMjQiOnRydWUsIjI1Ijp0cnVlLCIyNiI6dHJ1ZSwiMjciOnRydWUsIjI4Ijp0cnVlLCIyOSI6dHJ1ZSwiMyI6dHJ1ZSwiMzAiOnRydWUsIjMxIjp0cnVlLCIzMiI6dHJ1ZSwiMzMiOnRydWUsIjM0Ijp0cnVlLCIzNSI6dHJ1ZSwiMzYiOnRydWUsIjM3Ijp0cnVlLCIzOCI6dHJ1ZSwiMzkiOnRydWUsIjQiOnRydWUsIjQwIjp0cnVlLCI0MSI6dHJ1ZSwiNDIiOnRydWUsIjQzIjp0cnVlLCI0NCI6dHJ1ZSwiNDUiOnRydWUsIjQ2Ijp0cnVlLCI0NyI6dHJ1ZSwiNDgiOnRydWUsIjQ5Ijp0cnVlLCI1Ijp0cnVlLCI1MCI6dHJ1ZSwiNTEiOnRydWUsIjUyIjp0cnVlLCI1MyI6dHJ1ZSwiNTQiOnRydWUsIjU1Ijp0cnVlLCI1NiI6dHJ1ZSwiNTciOnRydWUsIjU4Ijp0cnVlLCI1OSI6dHJ1ZSwiNiI6dHJ1ZSwiNjAiOnRydWUsIjYxIjp0cnVlLCI2MiI6dHJ1ZSwiNjMiOnRydWUsIjY0Ijp0cnVlLCI2NSI6dHJ1ZSwiNjYiOnRydWUsIjY3Ijp0cnVlLCI2OCI6dHJ1ZSwiNjkiOnRydWUsIjciOnRydWUsIjcwIjp0cnVlLCI3MSI6dHJ1ZSwiNzIiOnRydWUsIjczIjp0cnVlLCI4Ijp0cnVlLCI5Ijp0cnVlfSwicHJval9yb2xlX2lkIjoiIiwicHJval9wZXJtaXNzaW9ucyI6e30sInByb2plY3RzIjpbXSwiZXhwIjoxNzQ4ODc3MzEzLCJpc3MiOiIxIn0.K30ii0WmaJ_9A7GoJPRWa7_8MZs4ANfeZ7TjX6Hdw3A','2025-06-01 22:15:14'),(2,'expire','Mon, 02 Jun 2025 15:15:13 GMT','2025-06-01 22:15:14'),(3,'state','1','2025-06-01 22:15:14');
/*!40000 ALTER TABLE `serverHttpAuthDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `serverHttpDB`
--

DROP TABLE IF EXISTS `serverHttpDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `serverHttpDB` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `parameter` varchar(30) NOT NULL,
  `type` varchar(30) NOT NULL,
  `data` varchar(100) NOT NULL,
  `createdAt` datetime NOT NULL DEFAULT current_timestamp(),
  `updatedAt` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `serverHttpDB`
--

LOCK TABLES `serverHttpDB` WRITE;
/*!40000 ALTER TABLE `serverHttpDB` DISABLE KEYS */;
INSERT INTO `serverHttpDB` VALUES (1,'Authentication','auth','1','/v1/auth/login/connex','2024-03-26 10:48:31','2025-03-21 11:24:40'),(2,'Receiver Data','receiver','1','/v1/projectnode/nodes/nodeid/sensors/monitoring-data','2024-03-26 10:48:31','2025-03-21 11:25:32'),(3,'Node Detail','node','1','/v1/projectnode/nodes/nodeid/connex','2024-03-26 10:48:31','2025-03-12 15:17:07'),(4,'Sensor Detail','sensor','1','/v1/projectnode/nodes/nodeid/sensors/connex','2024-03-26 10:48:31','2025-03-21 11:28:53'),(5,'Actuator Detail','actuator','1','/v1/projectnode/nodes/nodeid/actuators/connexs','2024-03-26 10:48:31','2025-06-01 22:21:19'),(6,'Notification','notif','1','/v1/notification','2024-03-26 10:49:15','2025-03-13 11:02:11'),(7,'Reboot','reboot','1','/v1/projectnode/nodes/nodeid/reboot','2024-03-26 10:49:15','2025-03-12 15:18:03'),(12,'Update','update','1','/v1/monitoring/updater','2024-06-05 15:38:07','2025-03-12 15:18:24');
/*!40000 ALTER TABLE `serverHttpDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `serverMqttDB`
--

DROP TABLE IF EXISTS `serverMqttDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `serverMqttDB` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `parameter` varchar(30) NOT NULL,
  `data` varchar(30) NOT NULL,
  `createdAt` datetime NOT NULL DEFAULT current_timestamp(),
  `updatedAt` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `serverMqttDB`
--

LOCK TABLES `serverMqttDB` WRITE;
/*!40000 ALTER TABLE `serverMqttDB` DISABLE KEYS */;
INSERT INTO `serverMqttDB` VALUES (1,'Publish Data Sensor','data','node/nodeid/data','2024-03-26 10:52:40','2024-12-03 22:29:55'),(2,'Node Detail','node','node/nodeid','2024-03-26 10:52:40','2024-12-03 22:30:08'),(3,'Sensor Detail','sensor','node/nodeid/sensors','2024-03-26 10:52:40','2024-12-03 22:30:20'),(4,'Actuator Detail','actuator','node/nodeid/actuators','2024-03-26 10:52:40','2024-12-03 22:30:30'),(5,'Notification','notif','notifications/node/nodeid','2024-03-26 10:52:40','2024-12-03 22:30:43');
/*!40000 ALTER TABLE `serverMqttDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `serverSettingDB`
--

DROP TABLE IF EXISTS `serverSettingDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `serverSettingDB` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `server` varchar(30) NOT NULL,
  `domainAddress` varchar(30) NOT NULL,
  `ipAddress` varchar(30) NOT NULL,
  `port` varchar(5) NOT NULL,
  `username` varchar(30) NOT NULL,
  `password` varchar(100) NOT NULL,
  `updatedAt` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `serverSettingDB`
--

LOCK TABLES `serverSettingDB` WRITE;
/*!40000 ALTER TABLE `serverSettingDB` DISABLE KEYS */;
INSERT INTO `serverSettingDB` VALUES (1,'http','api-nearon.synapsis.id','139.180.216.99','80','admin','password','2025-04-28 14:05:42'),(2,'mqtt','mqtt.synapsis.id','-','32100','synapsis','Rasp8266!','2025-01-20 13:38:08');
/*!40000 ALTER TABLE `serverSettingDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `systemServiceDB`
--

DROP TABLE IF EXISTS `systemServiceDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `systemServiceDB` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `service` varchar(20) NOT NULL,
  `enable` varchar(20) NOT NULL,
  `state` varchar(1000) DEFAULT '',
  `last_update` datetime DEFAULT NULL,
  `last_run` varchar(100) NOT NULL,
  `since` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `systemServiceDB`
--

LOCK TABLES `systemServiceDB` WRITE;
/*!40000 ALTER TABLE `systemServiceDB` DISABLE KEYS */;
INSERT INTO `systemServiceDB` VALUES (1,'nearon_dashboard','inactive','enabled','-',NULL,'Tue 2025-04-29 15:24:50','45min '),(2,'nearon_auth','active','enabled','Device Already Authentication with Server','2025-06-02 00:31:46','Mon 2025-06-02 00:31:39','8s '),(3,'nearon_routine','active','enabled','Feature Routine Monitoring Setting Inactive','2025-06-02 00:31:54','Mon 2025-06-02 00:31:40','9s '),(4,'nearon_alarm','active','enabled','Feature Alarm Monitoring Setting Inactive','2025-06-02 00:31:52','Mon 2025-06-02 00:31:49','1s '),(5,'nearon_buffer','active','enabled','Feature Buffer Monitoring Setting Inactive','2025-06-02 00:31:51','Mon 2025-06-02 00:31:48','2s '),(6,'nearon_sync','active','enabled','Feature Synchronize Sensor Option Setting Inactive','2025-06-02 00:31:54','Mon 2025-06-02 00:31:49','3s '),(7,'nearon_notif','active','enabled','Feature Notification Setting Inactive','2025-06-02 00:31:50','Mon 2025-06-02 00:31:47','5s '),(8,'nearon_log','active','enabled','Feature Routine Internal Log Setting Inactive','2025-06-02 00:31:54','Mon 2025-06-02 00:31:40','13s '),(9,'nearon_display','inactive','disabled','inactive',NULL,'-','-'),(11,'sensor2','active','enabled','2 Sensors Failed Sampling - 2 Port Error Device Offline (Port 1 Ext 1, Port 2 Ext 1)','2025-06-02 00:31:50','Tue 2025-04-29 16:28:25','1 months 2 days '),(12,'sensor3','active','enabled','8 Sensors Success Sampling','2025-06-02 01:06:01','Tue 2025-04-29 16:28:25','1 months 2 days '),(13,'sensor4','inactive','disabled','0 of 0 Sensors Failed Sampling','2025-03-12 14:55:07','-','-'),(14,'sensor5','inactive','disabled','3 Sensors Failed Sampling - HTTPConnectionPool(host=\'10.19.54.11\', port=80): Max retries exceeded with url: /api/set/remote/ac (Caused by NewConnectionError(\'<urllib3.connection.HTTPConnection object at 0x7faa3bce20>: Failed to establish a new connection: [Errno 113] No route to host\'))','2025-03-12 14:54:55','-','-'),(15,'sensor6','inactive','disabled','inactive','2025-04-27 22:51:33','-','-'),(16,'sensor7','inactive','disabled','inactive','2025-04-27 22:51:40','-','-'),(17,'sensor8','inactive','disabled','inactive',NULL,'-','-'),(24,'sensor1','active','enabled','8 Sensors Failed Sampling - HTTPConnectionPool(host=\'10.19.53.71\', port=80): Max retries exceeded with url: /measures/current (Caused by NewConnectionError(\'<urllib3.connection.HTTPConnection object at 0x7f96fbfa60>: Failed to establish a new connection: [Errno 113] No route to host\'))','2025-06-02 00:31:50','Mon 2025-06-02 00:31:41','12s '),(30,'actuator1','inactive','disabled','Service Error - KeyError (\'actuator_custom_id\')','2025-06-01 22:26:54','-','-'),(31,'actuator2','inactive','enabled','-',NULL,'','');
/*!40000 ALTER TABLE `systemServiceDB` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-06-02  0:31:55
