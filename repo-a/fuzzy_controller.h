#ifndef FUZZY_LOGIC_SETUP_H
#define FUZZY_LOGIC_SETUP_H

#include <Fuzzy.h>

/**
 * @brief Menginisialisasi dan mengkonfigurasi sistem logika fuzzy.
 * @param fuzzy Pointer ke objek Fuzzy yang akan dikonfigurasi.
 */
void initializeFuzzySystem(Fuzzy* fuzzy) {
  // --- Input: Temperatur & Kelembaban ---
  FuzzyInput* temperature = new FuzzyInput(1);
  FuzzySet* tempLow = new FuzzySet(26, 28, 30, 32);
  FuzzySet* tempMedium = new FuzzySet(31, 32, 34, 36);
  FuzzySet* tempHigh = new FuzzySet(35, 36, 50, 50);
  temperature->addFuzzySet(tempLow);
  temperature->addFuzzySet(tempMedium);
  temperature->addFuzzySet(tempHigh);
  fuzzy->addFuzzyInput(temperature);

  FuzzyInput* humidity = new FuzzyInput(2);
  FuzzySet* humLow = new FuzzySet(0, 0, 40, 60);
  FuzzySet* humMedium = new FuzzySet(55, 60, 70, 75);
  FuzzySet* humHigh = new FuzzySet(70, 75, 100, 100);
  humidity->addFuzzySet(humLow);
  humidity->addFuzzySet(humMedium);
  humidity->addFuzzySet(humHigh);
  fuzzy->addFuzzyInput(humidity);

  // --- Input Konsentrasi Gas (Digital) ---
  FuzzyInput* gasConcentration = new FuzzyInput(3);
  FuzzySet* gasDetected = new FuzzySet(1, 1, 1, 1);
  FuzzySet* gasSafe = new FuzzySet(0, 0, 0, 0);
  gasConcentration->addFuzzySet(gasDetected);
  gasConcentration->addFuzzySet(gasSafe);
  fuzzy->addFuzzyInput(gasConcentration);

  // --- Input Sensor Api (Digital) ---
  FuzzyInput* flame = new FuzzyInput(4);
  FuzzySet* fireDetected = new FuzzySet(0, 0, 0, 0);
  FuzzySet* noFire = new FuzzySet(1, 1, 1, 1);
  flame->addFuzzySet(fireDetected);
  flame->addFuzzySet(noFire);
  fuzzy->addFuzzyInput(flame);

  // --- Output: Kecepatan Kipas ---
  FuzzyOutput* fanSpeed = new FuzzyOutput(1);
  FuzzySet* fanOff = new FuzzySet(0, 0, 0, 0);
  FuzzySet* fanLow = new FuzzySet(80, 90, 110, 130);
  FuzzySet* fanMedium = new FuzzySet(130, 150, 170, 190);
  FuzzySet* fanHigh = new FuzzySet(190, 210, 255, 255);
  fanSpeed->addFuzzySet(fanOff);
  fanSpeed->addFuzzySet(fanLow);
  fanSpeed->addFuzzySet(fanMedium);
  fanSpeed->addFuzzySet(fanHigh);
  fuzzy->addFuzzyOutput(fanSpeed);
  
  // --- Aturan Fuzzy ---
  FuzzyRuleAntecedent* ifFire = new FuzzyRuleAntecedent(); ifFire->joinSingle(fireDetected);
  FuzzyRuleAntecedent* ifGas = new FuzzyRuleAntecedent(); ifGas->joinSingle(gasDetected);
  FuzzyRuleAntecedent* ifFireAndGas = new FuzzyRuleAntecedent(); ifFireAndGas->joinWithAND(ifFire, ifGas);
  FuzzyRuleConsequent* thenFanMaxEmergency = new FuzzyRuleConsequent(); thenFanMaxEmergency->addOutput(fanHigh);
  fuzzy->addFuzzyRule(new FuzzyRule(-1, ifFireAndGas, thenFanMaxEmergency));
  FuzzyRuleConsequent* thenFanHighForFire = new FuzzyRuleConsequent(); thenFanHighForFire->addOutput(fanHigh);
  fuzzy->addFuzzyRule(new FuzzyRule(0, ifFire, thenFanHighForFire));
  FuzzyRuleConsequent* thenFanHighForGas = new FuzzyRuleConsequent(); thenFanHighForGas->addOutput(fanHigh);
  fuzzy->addFuzzyRule(new FuzzyRule(1, ifGas, thenFanHighForGas));
  FuzzyRuleAntecedent* ifSafeCondition = new FuzzyRuleAntecedent(); ifSafeCondition->joinWithAND(noFire, gasSafe);
  FuzzyRuleAntecedent* humComfortable = new FuzzyRuleAntecedent(); humComfortable->joinWithOR(humLow, humMedium);
  FuzzyRuleAntecedent* ifComfortable = new FuzzyRuleAntecedent(); ifComfortable->joinWithAND(tempLow, humComfortable);
  FuzzyRuleAntecedent* ifComfortableAndSafe = new FuzzyRuleAntecedent(); ifComfortableAndSafe->joinWithAND(ifComfortable, ifSafeCondition);
  FuzzyRuleConsequent* thenFanOff = new FuzzyRuleConsequent(); thenFanOff->addOutput(fanOff);
  fuzzy->addFuzzyRule(new FuzzyRule(2, ifComfortableAndSafe, thenFanOff));
  FuzzyRuleAntecedent* ifComfortableButHumid = new FuzzyRuleAntecedent(); ifComfortableButHumid->joinWithAND(tempLow, humHigh);
  FuzzyRuleAntecedent* ifComfortableButHumidAndSafe = new FuzzyRuleAntecedent(); ifComfortableButHumidAndSafe->joinWithAND(ifComfortableButHumid, ifSafeCondition);
  FuzzyRuleConsequent* thenFanLow1 = new FuzzyRuleConsequent(); thenFanLow1->addOutput(fanLow);
  fuzzy->addFuzzyRule(new FuzzyRule(3, ifComfortableButHumidAndSafe, thenFanLow1));
  FuzzyRuleAntecedent* ifMediumTempDry = new FuzzyRuleAntecedent(); ifMediumTempDry->joinWithAND(tempMedium, humLow);
  FuzzyRuleAntecedent* ifMediumTempDryAndSafe = new FuzzyRuleAntecedent(); ifMediumTempDryAndSafe->joinWithAND(ifMediumTempDry, ifSafeCondition);
  FuzzyRuleConsequent* thenFanLow2 = new FuzzyRuleConsequent(); thenFanLow2->addOutput(fanLow);
  fuzzy->addFuzzyRule(new FuzzyRule(4, ifMediumTempDryAndSafe, thenFanLow2));
  FuzzyRuleAntecedent* humMedOrHigh = new FuzzyRuleAntecedent(); humMedOrHigh->joinWithOR(humMedium, humHigh);
  FuzzyRuleAntecedent* ifMediumTempHumid = new FuzzyRuleAntecedent(); ifMediumTempHumid->joinWithAND(tempMedium, humMedOrHigh);
  FuzzyRuleAntecedent* ifMediumTempHumidAndSafe = new FuzzyRuleAntecedent(); ifMediumTempHumidAndSafe->joinWithAND(ifMediumTempHumid, ifSafeCondition);
  FuzzyRuleConsequent* thenFanMedium = new FuzzyRuleConsequent(); thenFanMedium->addOutput(fanMedium);
  fuzzy->addFuzzyRule(new FuzzyRule(5, ifMediumTempHumidAndSafe, thenFanMedium));
  FuzzyRuleAntecedent* ifHighTemp = new FuzzyRuleAntecedent(); ifHighTemp->joinSingle(tempHigh);
  FuzzyRuleAntecedent* ifHighTempAndSafe = new FuzzyRuleAntecedent(); ifHighTempAndSafe->joinWithAND(ifHighTemp, ifSafeCondition);
  FuzzyRuleConsequent* thenFanHighForTemp = new FuzzyRuleConsequent(); thenFanHighForTemp->addOutput(fanHigh);
  fuzzy->addFuzzyRule(new FuzzyRule(6, ifHighTempAndSafe, thenFanHighForTemp));
}

#endif // FUZZY_LOGIC_SETUP_H